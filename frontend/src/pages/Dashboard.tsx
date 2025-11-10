/**
 * Dashboard page - main page for expense import workflow
 */
import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Tab,
  Tabs,
  Paper,
  Alert,
} from '@mui/material';
import FileUploader from '../components/FileUploader';
import ExpensePreview from '../components/ExpensePreview';
import ImportSummary from '../components/ImportSummary';
import { previewExpenseFile } from '../api/expenses';
import type { ExpenseData } from '../api/expenses';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
};

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [previewData, setPreviewData] = useState<ExpenseData[]>([]);
  const [previewFilename, setPreviewFilename] = useState<string>('');
  const [previewTotalRows, setPreviewTotalRows] = useState<number>(0);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handlePreview = async (file: File, year: string) => {
    setPreviewLoading(true);
    setPreviewError(null);
    setPreviewData([]);

    try {
      const result = await previewExpenseFile(file, year);
      setPreviewData(result.data);
      setPreviewFilename(result.filename);
      setPreviewTotalRows(result.total_rows);
      setActiveTab(1); // Switch to preview tab
    } catch (err: any) {
      setPreviewError(err.response?.data?.detail || err.message || 'Preview failed');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleUploadSuccess = (result: any) => {
    setImportResult(result);
    setActiveTab(2); // Switch to summary tab
    
    // Clear preview data
    setPreviewData([]);
    setPreviewFilename('');
    setPreviewTotalRows(0);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            💰 Smart Expense Importer
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Upload yearly expense Excel files and let AI normalize the data automatically
          </Typography>
        </Box>

        {/* Tabs */}
        <Paper elevation={2} sx={{ mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="dashboard tabs">
            <Tab label="Upload" />
            <Tab label="Preview" disabled={previewData.length === 0 && !previewLoading} />
            <Tab label="Summary" disabled={!importResult} />
          </Tabs>
        </Paper>

        {/* Tab Panels */}
        <TabPanel value={activeTab} index={0}>
          <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', md: 'row' } }}>
            <Box sx={{ flex: 2 }}>
              <FileUploader 
                onUploadSuccess={handleUploadSuccess}
                onPreview={handlePreview}
              />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  📋 Instructions
                </Typography>
                <Typography variant="body2" paragraph>
                  1. Enter the year of your expenses
                </Typography>
                <Typography variant="body2" paragraph>
                  2. Select an Excel file (.xlsx or .xls)
                </Typography>
                <Typography variant="body2" paragraph>
                  3. Click "Preview" to see normalized data
                </Typography>
                <Typography variant="body2" paragraph>
                  4. Click "Upload & Import" to save to database
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  <strong>Note:</strong> The AI will automatically detect and normalize
                  different column formats from your Excel files.
                </Typography>
              </Paper>
            </Box>
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {previewLoading ? (
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="body1">Loading preview...</Typography>
            </Paper>
          ) : previewError ? (
            <Alert severity="error" onClose={() => setPreviewError(null)}>
              {previewError}
            </Alert>
          ) : (
            <ExpensePreview
              data={previewData}
              filename={previewFilename}
              totalRows={previewTotalRows}
            />
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          {importResult && (
            <ImportSummary
              imported={importResult.imported}
              skipped={importResult.skipped}
              status={importResult.status}
              message={importResult.message}
            />
          )}
        </TabPanel>
      </Box>
    </Container>
  );
};

export default Dashboard;
