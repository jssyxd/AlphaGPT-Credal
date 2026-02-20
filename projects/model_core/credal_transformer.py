"""
Credal Transformer - 基于证据理论的Transformer模型
基于论文: arXiv 2510.12137 - Credal Transformer
使用Dirichlet分布替换Softmax，提供不确定性感知
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, Tuple, Dict, List
from sympy import symbols, sympify, simplify, Symbol
from sympy.parsing.sympy_parser import parse_expr
import json


class EvidenceQualityLayer(nn.Module):
    """
    证据质量计算层
    将注意力分数转换为证据质量: α_ij = exp(s_ij) + 1
    """
    def __init__(self, d_model: int, num_heads: int = 8):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads

        # 标准的Q, K, V投影
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)

        # 证据质量学习参数
        self.evidence_scale = nn.Parameter(torch.ones(1))
        self.evidence_bias = nn.Parameter(torch.zeros(1))

        self.out_proj = nn.Linear(d_model, d_model)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None):
        batch_size, seq_len, _ = x.shape

        # 投影
        Q = self.q_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)

        # 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(self.head_dim)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        # 转换为证据质量: α = exp(s) + 1
        evidence = torch.exp(scores) * self.evidence_scale + 1 + self.evidence_bias

        # 计算不确定性: U = L / sum(α), L是类别数
        L = seq_len
        uncertainty = L / evidence.sum(dim=-1, keepdim=True)

        # 使用Dirichlet分布进行归一化（替代Softmax）
        # 概率 = α / sum(α)
        dirichlet_probs = evidence / evidence.sum(dim=-1, keepdim=True)

        # 应用注意力
        attn_output = torch.matmul(dirichlet_probs, V)

        # 合并多头
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)

        output = self.out_proj(attn_output)

        return output, uncertainty.squeeze(-1)


class CredalTransformer(nn.Module):
    """
    Credal Transformer模型
    使用证据理论和Dirichlet分布提供不确定性感知
    """
    def __init__(
        self,
        d_model: int = 128,
        num_heads: int = 8,
        num_layers: int = 4,
        d_ff: int = 512,
        dropout: float = 0.1,
        uncertainty_threshold: float = 0.3
    ):
        super().__init__()

        self.d_model = d_model
        self.uncertainty_threshold = uncertainty_threshold

        # 输入嵌入
        self.input_proj = nn.Linear(d_model, d_model)

        # Credal Transformer层
        self.layers = nn.ModuleList([
            CredalTransformerLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        # 输出层
        self.output_proj = nn.Linear(d_model, d_model)
        self.uncertainty_head = nn.Linear(d_model, 1)

        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None):
        """
        前向传播

        Returns:
            output: 模型输出
            uncertainty: 不确定性分数 [batch, seq_len]
            should_abstain: 是否应该弃权 [batch, seq_len]
        """
        x = self.input_proj(x)
        x = self.dropout(x)

        total_uncertainty = 0

        for layer in self.layers:
            x, uncertainty = layer(x, mask)
            total_uncertainty += uncertainty

        # 平均不确定性
        avg_uncertainty = total_uncertainty / len(self.layers)

        x = self.layer_norm(x)
        output = self.output_proj(x)

        # 计算是否应该弃权（不确定性太高）
        should_abstain = avg_uncertainty > self.uncertainty_threshold

        return output, avg_uncertainty, should_abstain

    def get_confidence(self, uncertainty: torch.Tensor) -> torch.Tensor:
        """将不确定性转换为置信度 (1 - uncertainty)"""
        return 1.0 - torch.clamp(uncertainty, 0, 1)


class CredalTransformerLayer(nn.Module):
    """单个Credal Transformer层"""
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float):
        super().__init__()

        self.attention = EvidenceQualityLayer(d_model, num_heads)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model)
        )

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None):
        # 注意力子层
        attn_out, uncertainty = self.attention(self.norm1(x), mask)
        x = x + self.dropout(attn_out)

        # 前馈子层
        ff_out = self.feed_forward(self.norm2(x))
        x = x + self.dropout(ff_out)

        return x, uncertainty


class FactorGenerator:
    """
    因子生成器
    使用SymPy生成可解释的交易因子公式
    """

    def __init__(self):
        self.operators = {
            'price': self._price_op,
            'volume': self._volume_op,
            'liquidity': self._liquidity_op,
            'fomo': self._fomo_op,
            'momentum': self._momentum_op,
            'volatility': self._volatility_op,
            'ma': self._ma_op,
            'rsi': self._rsi_op,
            'bollinger': self._bollinger_op,
        }

    def generate_factor(self, features: Dict[str, np.ndarray], complexity_penalty: float = 0.1) -> Tuple[str, float]:
        """
        生成因子公式

        Args:
            features: 特征字典，包含price, volume等
            complexity_penalty: 公式复杂度惩罚系数

        Returns:
            formula: 因子公式字符串
            score: 因子得分
        """
        # 定义基础符号
        p, v, l, f = symbols('price volume liquidity fomo', real=True, positive=True)

        # 生成候选公式
        candidates = [
            ('fomo * liquidity / volume', 'f * l / v'),
            ('momentum * sqrt(liquidity)', 'momentum * sqrt(l)'),
            ('(price - ma20) / volatility', '(p - ma(p,20)) / vol(p,20)'),
            ('rsi(14) * liquidity_score', 'rsi(p,14) * l/100000'),
            ('volume * price_change / liquidity', 'v * delta(p,1) / l'),
            ('bollinger_lower * fomo', 'bb_lower(p,20,2) * f'),
            ('ma5_cross_ma20 * volume', 'cross(ma(p,5), ma(p,20)) * v'),
        ]

        best_formula = None
        best_score = -float('inf')

        for name, expr_str in candidates:
            try:
                # 计算因子得分（简化版：基于夏普比率模拟）
                score = self._evaluate_formula(name, features)

                # 应用复杂度惩罚
                complexity = len(name.split())
                penalized_score = score - complexity * complexity_penalty

                if penalized_score > best_score:
                    best_score = penalized_score
                    best_formula = name

            except Exception as e:
                continue

        return best_formula or 'liquidity * fomo / volume', max(best_score, 0.5)

    def _evaluate_formula(self, formula: str, features: Dict[str, np.ndarray]) -> float:
        """评估因子公式的历史表现（模拟）"""
        # 简化的评分逻辑
        # 实际应该基于历史回测

        # 流动性因子通常表现较好
        if 'liquidity' in formula and 'fomo' in formula:
            return 0.75
        elif 'momentum' in formula:
            return 0.70
        elif 'rsi' in formula or 'bollinger' in formula:
            return 0.65
        else:
            return 0.60

    def _price_op(self, data):
        return data.get('close', np.zeros(100))

    def _volume_op(self, data):
        return data.get('volume', np.zeros(100))

    def _liquidity_op(self, data):
        return data.get('liquidity', np.zeros(100))

    def _fomo_op(self, data):
        """FOMO分数：基于价格变化和交易量计算"""
        price = data.get('close', np.zeros(100))
        volume = data.get('volume', np.ones(100))

        if len(price) < 2:
            return np.ones_like(price)

        # 价格变化率
        price_change = np.diff(price, prepend=price[0]) / np.maximum(price, 1e-8)

        # FOMO = 价格变化 * 交易量归一化
        volume_norm = volume / np.maximum(volume.mean(), 1)
        fomo = np.abs(price_change) * volume_norm

        return fomo

    def _momentum_op(self, data, period=10):
        """动量指标"""
        price = data.get('close', np.zeros(100))
        if len(price) < period:
            return np.zeros_like(price)

        momentum = (price - np.roll(price, period)) / np.maximum(np.roll(price, period), 1e-8)
        return momentum

    def _volatility_op(self, data, period=20):
        """波动率指标"""
        price = data.get('close', np.zeros(100))
        if len(price) < period:
            return np.zeros_like(price)

        volatility = np.array([np.std(price[max(0,i-period):i+1]) for i in range(len(price))])
        return volatility

    def _ma_op(self, data, period=20):
        """移动平均线"""
        price = data.get('close', np.zeros(100))
        if len(price) < period:
            return price

        ma = np.convolve(price, np.ones(period)/period, mode='same')
        return ma

    def _rsi_op(self, data, period=14):
        """RSI指标"""
        price = data.get('close', np.zeros(100))
        if len(price) < period + 1:
            return np.ones_like(price) * 50

        delta = np.diff(price, prepend=price[0])
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)

        avg_gain = np.convolve(gain, np.ones(period)/period, mode='same')
        avg_loss = np.convolve(loss, np.ones(period)/period, mode='same')

        rs = avg_gain / np.maximum(avg_loss, 1e-8)
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _bollinger_op(self, data, period=20, std_dev=2):
        """布林带指标"""
        price = data.get('close', np.zeros(100))
        if len(price) < period:
            return price, price, price

        ma = self._ma_op(data, period)
        std = np.array([np.std(price[max(0,i-period):i+1]) for i in range(len(price))])

        upper = ma + std_dev * std
        lower = ma - std_dev * std

        return upper, ma, lower

    def formula_to_json(self, formula: str, score: float, uncertainty: float) -> str:
        """将因子公式转换为JSON格式存储"""
        return json.dumps({
            'formula': formula,
            'score': float(score),
            'uncertainty': float(uncertainty),
            'confidence': float(1 - uncertainty),
            'timestamp': str(np.datetime64('now'))
        })


class UncertaintyAwareStrategy:
    """
    不确定性感知策略
    使用Credal Transformer的输出生成交易信号
    """

    def __init__(self, model: CredalTransformer, generator: FactorGenerator):
        self.model = model
        self.generator = generator
        self.uncertainty_threshold = 0.3
        self.confidence_threshold = 0.7

    def generate_signal(
        self,
        features: torch.Tensor,
        token_info: Dict
    ) -> Dict:
        """
        生成交易信号

        Returns:
            {
                'action': 'buy'/'sell'/'hold',
                'confidence': float,
                'uncertainty': float,
                'factor': str,
                'should_abstain': bool
            }
        """
        with torch.no_grad():
            output, uncertainty, should_abstain = self.model(features.unsqueeze(0))

        confidence = 1.0 - uncertainty.item()

        # 如果不确定性太高，建议弃权
        if should_abstain.item() or confidence < self.confidence_threshold:
            return {
                'action': 'hold',
                'confidence': confidence,
                'uncertainty': uncertainty.item(),
                'factor': 'uncertainty_too_high',
                'should_abstain': True,
                'reason': '模型不确定性超过阈值'
            }

        # 生成因子
        factor_str, factor_score = self.generator.generate_factor(token_info)

        # 基于输出和因子决定行动
        signal_score = output.mean().item()

        if signal_score > 0.6 and factor_score > 0.6:
            action = 'buy'
        elif signal_score < 0.4:
            action = 'sell'
        else:
            action = 'hold'

        return {
            'action': action,
            'confidence': confidence,
            'uncertainty': uncertainty.item(),
            'factor': factor_str,
            'factor_score': factor_score,
            'should_abstain': False
        }


# 测试代码
if __name__ == "__main__":
    # 创建模型
    model = CredalTransformer(d_model=64, num_heads=4, num_layers=2)
    generator = FactorGenerator()
    strategy = UncertaintyAwareStrategy(model, generator)

    # 测试输入
    batch_size = 2
    seq_len = 10
    d_model = 64

    x = torch.randn(batch_size, seq_len, d_model)

    # 前向传播
    output, uncertainty, should_abstain = model(x)

    print(f"输出形状: {output.shape}")
    print(f"不确定性: {uncertainty}")
    print(f"是否弃权: {should_abstain}")

    # 测试因子生成
    test_features = {
        'close': np.random.randn(100) * 10 + 100,
        'volume': np.random.randn(100) * 1000 + 5000,
        'liquidity': np.random.randn(100) * 50000 + 100000,
    }

    formula, score = generator.generate_factor(test_features)
    print(f"\n生成的因子: {formula}")
    print(f"因子得分: {score:.2f}")

    # 测试策略
    signal = strategy.generate_signal(x[0], test_features)
    print(f"\n交易信号: {signal}")
