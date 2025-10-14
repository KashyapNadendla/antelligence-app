import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface BlockchainTransaction {
  tx_hash: string;
  step: number;
  position: number[];
  ant_type: string;
  submit_time: number;
  confirm_time: number;
  latency_ms: number;
  success: boolean;
  gas_used?: number;
  is_simulated?: boolean;  // Flag to indicate simulated fallback transactions
}

interface BlockchainMetricsProps {
  transactions: BlockchainTransaction[];
}

export function BlockchainMetrics({ transactions }: BlockchainMetricsProps) {
  // Filter out simulated transactions - only show real blockchain transactions
  const realTransactions = React.useMemo(() => {
    return transactions.filter(tx => !tx.is_simulated);
  }, [transactions]);

  // Calculate metrics
  const metrics = React.useMemo(() => {
    if (realTransactions.length === 0) {
      return {
        totalTx: 0,
        avgLatency: 0,
        minLatency: 0,
        maxLatency: 0,
        successRate: 100,
        llmTx: 0,
        ruleTx: 0,
      };
    }

    const latencies = realTransactions.map(tx => tx.latency_ms);
    const avgLatency = latencies.reduce((sum, val) => sum + val, 0) / latencies.length;
    const minLatency = Math.min(...latencies);
    const maxLatency = Math.max(...latencies);
    const successCount = realTransactions.filter(tx => tx.success).length;
    const successRate = (successCount / realTransactions.length) * 100;
    const llmTx = realTransactions.filter(tx => tx.ant_type === 'LLM').length;
    const ruleTx = realTransactions.filter(tx => tx.ant_type === 'Rule').length;

    return {
      totalTx: realTransactions.length,
      avgLatency: Math.round(avgLatency),
      minLatency,
      maxLatency,
      successRate: Math.round(successRate),
      llmTx,
      ruleTx,
    };
  }, [realTransactions]);

  // Prepare chart data - sample every Nth transaction to keep chart readable
  const chartData = React.useMemo(() => {
    if (realTransactions.length === 0) return [];
    
    // Sample up to 20 points for a clean chart
    const sampleRate = Math.max(1, Math.floor(realTransactions.length / 20));
    return realTransactions
      .filter((_, index) => index % sampleRate === 0)
      .map(tx => ({
        step: tx.step,
        latency: tx.latency_ms,
        type: tx.ant_type,
      }));
  }, [realTransactions]);

  if (realTransactions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>🔗 Blockchain Metrics</CardTitle>
          <CardDescription>
            Transaction latency and throughput data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6 text-muted-foreground">
            <p>No blockchain transactions recorded yet</p>
            <p className="text-sm mt-2">Run a simulation to see blockchain analytics</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>🔗 Blockchain Transaction Analytics</CardTitle>
        <CardDescription>
          Latency and throughput metrics for {metrics.totalTx} transactions
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Compact Metrics Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div className="p-3 rounded-lg border bg-card/50">
            <div className="text-xs text-muted-foreground">Avg Latency</div>
            <div className="text-xl font-bold text-blue-600">{metrics.avgLatency}ms</div>
          </div>
          <div className="p-3 rounded-lg border bg-card/50">
            <div className="text-xs text-muted-foreground">Range</div>
            <div className="text-sm font-semibold">{metrics.minLatency}-{metrics.maxLatency}ms</div>
          </div>
          <div className="p-3 rounded-lg border bg-card/50">
            <div className="text-xs text-muted-foreground">Success Rate</div>
            <div className="text-xl font-bold text-green-600">{metrics.successRate}%</div>
          </div>
          <div className="p-3 rounded-lg border bg-card/50">
            <div className="text-xs text-muted-foreground">Throughput</div>
            <div className="text-sm font-semibold">
              <span className="text-purple-600">{metrics.llmTx} LLM</span>
              <span className="mx-1">/</span>
              <span className="text-blue-600">{metrics.ruleTx} Rule</span>
            </div>
          </div>
        </div>

        {/* Compact Latency Chart */}
        <div className="mt-4">
          <div className="text-sm font-medium mb-2">Transaction Latency Over Time</div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis 
                dataKey="step" 
                label={{ value: 'Step', position: 'insideBottom', offset: -5 }}
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                label={{ value: 'Latency (ms)', angle: -90, position: 'insideLeft' }}
                tick={{ fontSize: 12 }}
              />
              <Tooltip 
                formatter={(value: any, name: string) => {
                  if (name === 'latency') return [`${value}ms`, 'Latency'];
                  return [value, name];
                }}
                labelFormatter={(label) => `Step: ${label}`}
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Line 
                type="monotone" 
                dataKey="latency" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={{ r: 3 }}
                name="Transaction Latency"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Compact Summary */}
        <div className="mt-3 text-xs text-muted-foreground text-center">
          {metrics.totalTx} total transactions • {metrics.llmTx} from LLM ants • {metrics.ruleTx} from Rule ants
        </div>

        {/* Recent Transactions with Etherscan Links */}
        <div className="mt-4">
          <div className="text-sm font-medium mb-2">Recent Transactions</div>
          <div className="max-h-[200px] overflow-y-auto space-y-1">
            {realTransactions.slice(-10).reverse().map((tx, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs p-2 rounded border bg-card/30 hover:bg-card/50 transition-colors">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                    tx.ant_type === 'LLM' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
                  }`}>
                    {tx.ant_type}
                  </span>
                  <span className="text-muted-foreground">Step {tx.step}</span>
                  <span className="text-muted-foreground truncate flex-1 min-w-0" title={tx.tx_hash}>
                    {tx.tx_hash.slice(0, 10)}...{tx.tx_hash.slice(-8)}
                  </span>
                  <span className={`${tx.success ? 'text-green-600' : 'text-red-600'}`}>
                    {tx.latency_ms}ms
                  </span>
                </div>
                <a
                  href={`https://sepolia.basescan.org/tx/${tx.tx_hash.startsWith('0x') ? tx.tx_hash : '0x' + tx.tx_hash}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ml-2 px-2 py-1 text-[10px] bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors whitespace-nowrap"
                >
                  View on Basescan
                </a>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

