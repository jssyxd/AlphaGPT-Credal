import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

const supabase = createClient(supabaseUrl, supabaseKey);

export async function GET() {
  try {
    // 获取持仓
    const { data: positions, error: posError } = await supabase
      .from('positions')
      .select('*')
      .eq('status', 'open')
      .order('entry_time', { ascending: false });

    if (posError) throw posError;

    // 获取最新信号
    const { data: signals, error: sigError } = await supabase
      .from('signals')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10);

    if (sigError) throw sigError;

    // 获取交易日志
    const { data: trades, error: tradeError } = await supabase
      .from('trade_logs')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(20);

    if (tradeError) throw tradeError;

    return NextResponse.json({
      positions: positions || [],
      signals: signals || [],
      trades: trades || [],
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data' },
      { status: 500 }
    );
  }
}
