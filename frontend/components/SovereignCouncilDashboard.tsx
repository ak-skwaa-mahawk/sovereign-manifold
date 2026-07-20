import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';

interface TelemetryPoint {
  block: number;
  vitality: number;
  h_band: number;
  curvature: number;
  dampening: number;
}

interface CryptographicProof {
  sha256: string;
  ledger_anchor: string;
}

interface BriefingPayload {
  timestamp: string;
  status: string;
  vitality: number;
  briefing_narrative: string;
  cryptographic_proof: CryptographicProof;
  quantities_before?: Record<string, number>;
  quantities_after?: Record<string, number>;
}

export const SovereignCouncilDashboard: React.FC = () => {
  const [telemetry, setTelemetry] = useState<TelemetryPoint[]>([]);
  const [activeBriefing, setActiveBriefing] = useState<BriefingPayload | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchLatestLedgerState = () => {
      try {
        const simulatedPoints: TelemetryPoint[] = [
          { block: 1, vitality: 0.9343, h_band: 3.0588, curvature: 0.892, dampening: 0.6351 },
          { block: 2, vitality: 0.9412, h_band: 3.0612, curvature: 0.895, dampening: 0.6353 },
          { block: 3, vitality: 0.9504, h_band: 3.0645, curvature: 0.889, dampening: 0.6356 },
          { block: 4, vitality: 0.9614, h_band: 3.0678, curvature: 0.892, dampening: 0.6355 }
        ];

        const simulatedBriefing: BriefingPayload = {
          timestamp: new Date().toISOString(),
          status: "APPROVED",
          vitality: 0.9614,
          briefing_narrative: "Consensus loop completed successfully. The living manifold vitality tracking maintains structural headroom under living pi_r boundaries. Ledger signature verification checked and approved.",
          cryptographic_proof: {
            sha256: "bf9374b808e49b5cc40794d6c572225883a886815158ff2547dfb8f044ec5336",
            ledger_anchor: "61315b99d66734358e72027f346282d3a7e3f4dc4d2cb5bbb00241af9db94aa6"
          },
          quantities_before: {
            "waterproofing_membrane": 1240.99,
            "insulation_board": 891.21,
            "sealant_cartridges": 156.12
          },
          quantities_after: {
            "waterproofing_membrane": 1241.75,
            "insulation_board": 891.76,
            "sealant_cartridges": 156.22
          }
        };

        setTelemetry(simulatedPoints);
        setActiveBriefing(simulatedBriefing);
        setLoading(false);
      } catch (error) {
        console.error("Ledger state ingestion link disrupted:", error);
      }
    };

    fetchLatestLedgerState();
    const streamInterval = setInterval(fetchLatestLedgerState, 5000);
    return () => clearInterval(streamInterval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#0a0a0f] text-white">
        <p className="font-mono text-sm animate-pulse">Ingesting cryptographically signed ledger state telemetry...</p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-[#0a0a0f] text-gray-100 min-h-screen font-sans">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-gray-800 pb-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">5D Sovereign Council Dashboard</h1>
          <p className="text-xs text-gray-400 font-mono mt-1">Node Status: OPERATIONAL // Ledger Sync Locked</p>
        </div>
        {activeBriefing && (
          <div className="mt-3 md:mt-0 px-3 py-1 bg-gray-900 border border-gray-800 rounded font-mono text-xs">
            System Vitality Score: <span className="text-[#00d4ff] font-bold">{activeBriefing.vitality.toFixed(4)}</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2 bg-[#121218] border border-gray-800 p-5 rounded-xl shadow-lg">
          <h3 className="text-sm font-semibold text-gray-300 font-mono mb-4">Living π_r Vitality Waveform</h3>
          <div className="w-100 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={telemetry} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f1f2e" />
                <XAxis dataKey="block" stroke="#6b7280" />
                <YAxis domain={[0.85, 1.05]} stroke="#6b7280" />
                <Tooltip contentStyle={{ backgroundColor: '#121218', borderColor: '#374151' }} />
                <ReferenceLine y={0.9999} stroke="#ef4444" strokeDasharray="4 4" label={{ value: "Veto Upper Floor", fill: "#ef4444", position: "top" }} />
                <Line type="monotone" dataKey="vitality" stroke="#00d4ff" strokeWidth={2.5} activeDot={{ r: 6 }} name="Vitality Scale" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-[#121218] border border-gray-800 p-5 rounded-xl shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-sm font-semibold text-gray-300 font-mono">Consensus Briefing Output</h3>
              {activeBriefing && (
                <span className="px-2 py-0.5 text-[10px] uppercase font-mono tracking-widest bg-emerald-950 text-emerald-400 border border-emerald-800 rounded">
                  {activeBriefing.status}
                </span>
              )}
            </div>
            {activeBriefing ? (
              <div className="space-y-3 font-mono text-xs text-gray-300 leading-relaxed">
                <p className="bg-gray-950 p-3 border border-gray-900 rounded text-gray-400">
                  {activeBriefing.briefing_narrative}
                </p>
                <div className="text-[10px] text-gray-500 space-y-1">
                  <p className="truncate"><strong>Manifest Proof:</strong> {activeBriefing.cryptographic_proof.sha256}</p>
                  <p className="truncate"><strong>Ledger Anchor:</strong> {activeBriefing.cryptographic_proof.ledger_anchor}</p>
                </div>
              </div>
            ) : (
              <p className="text-xs text-gray-500 font-mono">No telemetry report cached.</p>
            )}
          </div>
          <div className="mt-4 pt-3 border-t border-t-gray-900 text-[10px] text-gray-500 font-mono">
            Timestamp: {activeBriefing?.timestamp || "N/A"}
          </div>
        </div>
      </div>

      <div className="bg-[#121218] border border-gray-800 p-5 rounded-xl shadow-lg">
        <h3 className="text-sm font-semibold text-gray-300 font-mono mb-4">Resonance Adjusted Estimation Manifest</h3>
        {activeBriefing?.quantities_before ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse font-mono text-xs text-gray-400">
              <thead>
                <tr className="border-b border-gray-800 text-gray-300">
                  <th className="py-2 px-3">Material Identifier Segment</th>
                  <th className="py-2 px-3 text-right">Raw Estimation Qty</th>
                  <th className="py-2 px-3 text-right text-[#00d4ff]">Resonance Adjusted Qty</th>
                  <th className="py-2 px-3 text-right text-emerald-400">Structural Drift Shift</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(activeBriefing.quantities_before).map((material) => {
                  const before = activeBriefing.quantities_before![material];
                  const after = activeBriefing.quantities_after![material];
                  const variance = after - before;
                  return (
                    <tr key={material} className="border-b border-gray-900 hover:bg-gray-900/40">
                      <td className="py-2 px-3 text-gray-200 font-medium">{material.replace(/_/g, ' ')}</td>
                      <td className="py-2 px-3 text-right">{before.toFixed(2)}</td>
                      <td className="py-2 px-3 text-right text-white font-semibold">{after.toFixed(2)}</td>
                      <td className="py-2 px-3 text-right text-emerald-500">+{variance.toFixed(2)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs text-gray-500 font-mono">No active procurement shifts running.</p>
        )}
      </div>
    </div>
  );
};
