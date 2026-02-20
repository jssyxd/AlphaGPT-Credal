'use client';

import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Activity,
  TrendingUp,
  TrendingDown,
  Wallet,
  Zap,
  Target,
  Clock,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';

// Types
interface WalletInfo {
  address: string;
  balance: number;
  balanceUsd: number;
}

interface Position {
  id: number;
  token_address: string;
  symbol: string;
  entry_price: number;
  entry_time: string;
  amount_sol: number;
  amount_tokens: number;
  current_price?: number;
  pnl?: number;
  pnl_pct?: number;
}

interface Signal {
  id: number;
  token_address: string;
  symbol: string;
  score: number;
  created_at: string;
}

interface Strategy {
  name: string;
  formula_readable: string;
  score: number;
}

// API 基础 URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export default function DashboardPage() {
  const [wallet, setWallet] = useState<WalletInfo | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // 模拟数据（实际环境从后端API获取）
  const mockWallet: WalletInfo = {
    address: '5QQZG...kfxx',
    balance: 0.32,
    balanceUsd: 192,
  };

  const mockPositions: Position[] = [
    {
      id: 1,
      token_address: 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
      symbol: 'BONK',
      entry_price: 0.00002847,
      entry_time: '2024-02-20 10:30:00',
      amount_sol: 0.1,
      amount_tokens: 3512500,
      current_price: 0.0000312,
      pnl: 0.0096,
      pnl_pct: 9.6,
    },
  ];

  const mockSignals: Signal[] = [
    { id: 1, token_address: 'EPjFW...', symbol: 'USDC', score: 0.85, created_at: '2024-02-20 12:00:00' },
    { id: 2, token_address: 'JUP...', symbol: 'JUP', score: 0.78, created_at: '2024-02-20 11:55:00' },
    { id: 3, token_address: 'WIF...', symbol: 'WIF', score: 0.72, created_at: '2024-02-20 11:50:00' },
  ];

  const mockStrategy: Strategy = {
    name: 'meme_momentum_v1',
    formula_readable: 'fomo * liq_score',
    score: 0.72,
  };

  useEffect(() => {
    // 模拟数据加载
    const timer = setTimeout(() => {
      setWallet(mockWallet);
      setPositions(mockPositions);
      setSignals(mockSignals);
      setStrategy(mockStrategy);
      setLoading(false);
      setLastUpdate(new Date());
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const refreshData = () => {
    setLoading(true);
    setError(null);
    setTimeout(() => {
      setLastUpdate(new Date());
      setLoading(false);
    }, 1000);
  };

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <Card className="w-full max-w-md bg-slate-800/50 border-slate-700">
          <CardContent className="pt-6 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">连接错误</h2>
            <p className="text-slate-400 mb-4">{error}</p>
            <Button onClick={refreshData} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              重试
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  AlphaGPT
                </h1>
                <p className="text-xs text-slate-400">Solana Meme Trading</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <Clock className="h-4 w-4" />
                <span>更新: {lastUpdate.toLocaleTimeString()}</span>
              </div>
              <Button
                onClick={refreshData}
                variant="outline"
                size="sm"
                className="border-slate-600 hover:bg-slate-700"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              </Button>
              <Badge variant="outline" className="border-green-500 text-green-400">
                <Activity className="h-3 w-3 mr-1" />
                Live
              </Badge>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Wallet Balance */}
          <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">钱包余额</CardTitle>
              <Wallet className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-8 w-24 bg-slate-700" />
              ) : (
                <>
                  <div className="text-2xl font-bold text-white">{wallet?.balance.toFixed(4)} SOL</div>
                  <p className="text-xs text-slate-400">≈ ${wallet?.balanceUsd.toFixed(2)} USD</p>
                </>
              )}
            </CardContent>
          </Card>

          {/* Total PnL */}
          <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">总盈亏</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-8 w-24 bg-slate-700" />
              ) : (
                <>
                  <div className="text-2xl font-bold text-green-400">
                    +{(positions.reduce((sum, p) => sum + (p.pnl || 0), 0) * 100).toFixed(2)}%
                  </div>
                  <p className="text-xs text-slate-400">本期收益</p>
                </>
              )}
            </CardContent>
          </Card>

          {/* Open Positions */}
          <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">持仓数量</CardTitle>
              <Target className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-8 w-16 bg-slate-700" />
              ) : (
                <>
                  <div className="text-2xl font-bold text-white">{positions.length}</div>
                  <p className="text-xs text-slate-400">最多 2 个</p>
                </>
              )}
            </CardContent>
          </Card>

          {/* Strategy Score */}
          <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">策略评分</CardTitle>
              <Activity className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-8 w-16 bg-slate-700" />
              ) : (
                <>
                  <div className="text-2xl font-bold text-yellow-400">{((strategy?.score || 0) * 100).toFixed(0)}%</div>
                  <Progress value={(strategy?.score || 0) * 100} className="h-1 mt-2" />
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Positions */}
          <Card className="lg:col-span-2 bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-purple-400" />
                当前持仓
              </CardTitle>
              <CardDescription className="text-slate-400">
                实时跟踪您的 meme 币持仓
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-2">
                  {[1, 2].map((i) => (
                    <Skeleton key={i} className="h-12 w-full bg-slate-700" />
                  ))}
                </div>
              ) : positions.length === 0 ? (
                <div className="text-center py-8 text-slate-400">
                  <Target className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>暂无持仓</p>
                  <p className="text-sm">等待 AI 信号...</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow className="border-slate-700 hover:bg-slate-700/50">
                      <TableHead className="text-slate-400">代币</TableHead>
                      <TableHead className="text-slate-400">入场价</TableHead>
                      <TableHead className="text-slate-400">数量 (SOL)</TableHead>
                      <TableHead className="text-slate-400">盈亏</TableHead>
                      <TableHead className="text-slate-400">状态</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {positions.map((pos) => (
                      <TableRow key={pos.id} className="border-slate-700 hover:bg-slate-700/50">
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-xs font-bold">
                              {pos.symbol.slice(0, 2)}
                            </div>
                            <div>
                              <div className="font-semibold">{pos.symbol}</div>
                              <div className="text-xs text-slate-400">{pos.token_address.slice(0, 8)}...</div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>{pos.entry_price.toExponential(2)}</TableCell>
                        <TableCell>{pos.amount_sol.toFixed(4)}</TableCell>
                        <TableCell>
                          <div className={`flex items-center gap-1 ${(pos.pnl_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {(pos.pnl_pct || 0) >= 0 ? (
                              <TrendingUp className="h-4 w-4" />
                            ) : (
                              <TrendingDown className="h-4 w-4" />
                            )}
                            <span>{(pos.pnl_pct || 0).toFixed(2)}%</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="border-green-500 text-green-400">
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            持有中
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Signals */}
          <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-400" />
                最新信号
              </CardTitle>
              <CardDescription className="text-slate-400">
                AI 生成的交易信号
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-16 w-full bg-slate-700" />
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {signals.map((signal) => (
                    <div
                      key={signal.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center text-sm font-bold">
                          {signal.symbol.slice(0, 2)}
                        </div>
                        <div>
                          <div className="font-semibold">{signal.symbol}</div>
                          <div className="text-xs text-slate-400">{signal.created_at}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-green-400">
                          {(signal.score * 100).toFixed(0)}%
                        </div>
                        <Progress value={signal.score * 100} className="h-1 w-16" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Strategy Info */}
        <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-400" />
              当前策略
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-20 w-full bg-slate-700" />
            ) : (
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">策略名称:</span>
                  <Badge variant="secondary">{strategy?.name}</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">公式:</span>
                  <code className="px-2 py-1 rounded bg-slate-700 text-purple-300 font-mono">
                    {strategy?.formula_readable}
                  </code>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">评分:</span>
                  <span className="text-green-400 font-bold">
                    {((strategy?.score || 0) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Risk Warning */}
        <Card className="bg-red-900/20 border-red-800/50">
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-400 mt-0.5" />
              <div>
                <h4 className="font-semibold text-red-400">风险提示</h4>
                <p className="text-sm text-slate-400 mt-1">
                  Meme 币交易具有极高风险，可能在短时间内损失全部本金。本系统仅供测试和学习目的，
                  不构成任何投资建议。请确保您了解所有风险后再进行交易。
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
