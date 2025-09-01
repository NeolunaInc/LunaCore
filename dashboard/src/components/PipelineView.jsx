import React, { useState, useEffect } from 'react';

const PipelineView = () => {
  const [pipelines, setPipelines] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading pipeline data
    const loadPipelines = async () => {
      setLoading(true);
      // Mock data for now
      setTimeout(() => {
        setPipelines([
          {
            id: 'pipeline-1',
            name: 'Data Processing Pipeline',
            status: 'running',
            steps: [
              { id: 'step-1', name: 'Data Ingestion', status: 'completed' },
              { id: 'step-2', name: 'Data Validation', status: 'running' },
              { id: 'step-3', name: 'Data Processing', status: 'pending' },
            ]
          },
          {
            id: 'pipeline-2',
            name: 'ML Training Pipeline',
            status: 'idle',
            steps: [
              { id: 'step-4', name: 'Model Training', status: 'pending' },
              { id: 'step-5', name: 'Model Evaluation', status: 'pending' },
            ]
          }
        ]);
        setLoading(false);
      }, 1000);
    };

    loadPipelines();
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'running': return 'text-blue-600';
      case 'pending': return 'text-yellow-600';
      case 'failed': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✅';
      case 'running': return '🔄';
      case 'pending': return '⏳';
      case 'failed': return '❌';
      default: return '❓';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading pipelines...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">LunaCore Dashboard</h1>
      <h2 className="text-xl font-semibold mb-4">Pipeline Overview</h2>

      <div className="space-y-4">
        {pipelines.map((pipeline) => (
          <div key={pipeline.id} className="border rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-medium">{pipeline.name}</h3>
              <span className={`px-2 py-1 rounded text-sm ${getStatusColor(pipeline.status)}`}>
                {getStatusIcon(pipeline.status)} {pipeline.status}
              </span>
            </div>

            <div className="space-y-2">
              {pipeline.steps.map((step) => (
                <div key={step.id} className="flex items-center space-x-2">
                  <span className={getStatusColor(step.status)}>
                    {getStatusIcon(step.status)}
                  </span>
                  <span className="text-sm">{step.name}</span>
                  <span className={`text-xs px-2 py-1 rounded ${getStatusColor(step.status)}`}>
                    {step.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 p-4 bg-gray-100 rounded-lg">
        <h3 className="font-semibold mb-2">Phase 13: Dashboard Development</h3>
        <p className="text-sm text-gray-600">
          This is a basic React dashboard for monitoring LunaCore pipelines.
          Future enhancements will include real-time updates, detailed metrics,
          and interactive controls.
        </p>
      </div>
    </div>
  );
};

export default PipelineView;
