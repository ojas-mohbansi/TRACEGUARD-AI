import React, { useState } from 'react';
import {
  Upload,
  Download,
  Database,
  FileText,
  CheckCircle2,
  Calendar,
  Layers,
  FileCode,
  Tag,
  ArrowUpRight
} from 'lucide-react';
import api from '../services/api';
import { useApi } from '../hooks/useApi';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';

export function Datasets() {
  const { data: datasetsData, loading, error, refetch } = useApi(() => api.getDatasets());

  const [uploadFile, setUploadFile] = useState(null);
  const [datasetName, setDatasetName] = useState('');
  const [datasetDesc, setDatasetDesc] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setUploadFile(file);
      if (!datasetName) {
        setDatasetName(file.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      alert('Please select a CSV or JSON file to upload.');
      return;
    }

    setUploading(true);
    setUploadSuccess(null);

    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('name', datasetName || uploadFile.name);
    formData.append('description', datasetDesc);

    try {
      const res = await api.uploadDataset(formData);
      setUploadSuccess(`Dataset "${res.name}" registered successfully.`);
      setUploadFile(null);
      setDatasetName('');
      setDatasetDesc('');
      refetch();
    } catch (err) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const datasets = datasetsData?.datasets || [];

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--tg-border-subtle)]">
        <div>
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-[var(--tg-accent-emerald)]" />
            <h1 className="text-lg font-semibold tracking-tight text-[var(--tg-text-primary)]">
              Dataset Registry & Corpus
            </h1>
          </div>
          <p className="text-xs text-[var(--tg-text-muted)] mt-1">
            Manage protocol captures, synthetic evaluation suites, and ground-truth benchmark datasets.
          </p>
        </div>
      </div>

      {/* Dataset Ingestion Form */}
      <div className="tg-panel p-5 space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-[var(--tg-border-subtle)]">
          <Upload className="w-4 h-4 text-[var(--tg-accent-emerald)]" />
          <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
            Ingest Benchmark Corpus (CSV / JSON)
          </h2>
        </div>

        <form onSubmit={handleUpload} className="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
          <div className="md:col-span-4">
            <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
              Dataset Identifier
            </label>
            <input
              type="text"
              placeholder="e.g., cse_cic_ids2018_sample"
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              className="tg-input text-xs font-mono"
            />
          </div>

          <div className="md:col-span-5">
            <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
              Capture Description & Provenance
            </label>
            <input
              type="text"
              placeholder="e.g., Synthetic mixed protocol trace with 25% FSM violations"
              value={datasetDesc}
              onChange={(e) => setDatasetDesc(e.target.value)}
              className="tg-input text-xs font-mono"
            />
          </div>

          <div className="md:col-span-3 flex gap-2">
            <label className="flex-1 cursor-pointer tg-btn-secondary text-xs truncate">
              <span className="truncate">{uploadFile ? uploadFile.name : 'Choose File'}</span>
              <input
                type="file"
                accept=".csv,.json"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
            <button
              type="submit"
              disabled={uploading || !uploadFile}
              className="tg-btn-primary text-xs disabled:opacity-40"
            >
              {uploading ? 'Ingesting...' : 'Register'}
            </button>
          </div>
        </form>

        {uploadSuccess && (
          <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono text-[var(--tg-accent-emerald)] font-semibold flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>{uploadSuccess}</span>
          </div>
        )}
      </div>

      {/* Dataset Inventory Table */}
      <div className="tg-panel p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[var(--tg-border-subtle)]">
          <div>
            <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
              Registered Corpus Inventory ({datasets.length})
            </h2>
            <p className="text-[11px] text-[var(--tg-text-muted)] mt-0.5">
              Available sets for training, cross-validation, and multi-engine detection runs
            </p>
          </div>
        </div>

        {loading && !datasetsData ? (
          <LoadingSpinner text="Retrieving registered corpus..." />
        ) : (
          <div className="tg-table-container">
            <table className="tg-table">
              <thead>
                <tr>
                  <th>Dataset Name</th>
                  <th>Format</th>
                  <th>Volume</th>
                  <th>Created</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {datasets.length > 0 ? (
                  datasets.map((ds) => (
                    <tr key={ds.dataset_id}>
                      <td>
                        <div className="font-mono text-xs font-semibold text-[var(--tg-text-primary)]">
                          {ds.name}
                        </div>
                        {ds.description && (
                          <div className="text-[11px] text-[var(--tg-text-muted)] truncate max-w-sm">
                            {ds.description}
                          </div>
                        )}
                      </td>
                      <td>
                        <span className="tg-badge tg-badge-neutral">
                          {ds.format || 'CSV'}
                        </span>
                      </td>
                      <td className="font-mono text-xs text-[var(--tg-text-secondary)]">
                        {ds.session_count !== undefined
                          ? `${ds.session_count.toLocaleString()} sessions`
                          : ds.event_count !== undefined
                          ? `${ds.event_count.toLocaleString()} events`
                          : '—'}
                      </td>
                      <td className="font-mono text-xs text-[var(--tg-text-muted)]">
                        {ds.created_at ? new Date(ds.created_at).toLocaleDateString() : '—'}
                      </td>
                      <td>
                        <span className="tg-badge tg-badge-emerald">
                          Active
                        </span>
                      </td>
                      <td>
                        <a
                          href={api.getDatasetDownloadUrl ? api.getDatasetDownloadUrl(ds.dataset_id) : `#`}
                          download
                          className="text-xs font-mono text-[var(--tg-text-muted)] hover:text-[var(--tg-accent-emerald)] inline-flex items-center gap-1 transition"
                        >
                          <span>Export</span>
                          <ArrowUpRight className="w-3 h-3" />
                        </a>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="text-center py-8 text-xs text-[var(--tg-text-muted)]">
                      No datasets registered yet. Upload a CSV or JSON protocol log above.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Datasets;
