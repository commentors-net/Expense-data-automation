/**
 * File uploader component for Excel expense files
 */
import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  LinearProgress,
  Alert,
  Paper,
} from '@mui/material';
import { CloudUpload as UploadIcon } from '@mui/icons-material';
import { uploadExpenseFile } from '../api/expenses';

interface FileUploaderProps {
  onUploadSuccess?: (result: any) => void;
  onPreview?: (file: File, year: string) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onUploadSuccess, onPreview }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [year, setYear] = useState<string>(new Date().getFullYear().toString());
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
      ];
      if (!validTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls)$/i)) {
        setError('Please select a valid Excel file (.xlsx or .xls)');
        setSelectedFile(null);
        return;
      }

      // Validate file size (5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        setSelectedFile(null);
        return;
      }

      setSelectedFile(file);
      setError(null);
      setSuccess(null);
    }
  };

  const handleYearChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    // Only allow 4-digit numbers
    if (value === '' || (/^\d{0,4}$/.test(value))) {
      setYear(value);
      setError(null);
    }
  };

  const handlePreview = () => {
    if (!selectedFile || !year || year.length !== 4) {
      setError('Please select a file and enter a valid 4-digit year');
      return;
    }
    
    if (onPreview) {
      onPreview(selectedFile, year);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    if (!year || year.length !== 4) {
      setError('Please enter a valid 4-digit year');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);
    setProgress(0);

    try {
      const result = await uploadExpenseFile(selectedFile, year, setProgress);

      if (result.status === 'ok') {
        setSuccess(
          `Successfully imported ${result.imported} expense(s). ${
            result.skipped > 0 ? `Skipped ${result.skipped}.` : ''
          }`
        );
        setSelectedFile(null);
        setProgress(0);
        
        // Reset file input
        const fileInput = document.getElementById('file-input') as HTMLInputElement;
        if (fileInput) {
          fileInput.value = '';
        }

        if (onUploadSuccess) {
          onUploadSuccess(result);
        }
      } else {
        setError(result.message || 'Upload failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Upload Expense File
      </Typography>
      
      <Box sx={{ mt: 3 }}>
        <TextField
          label="Year"
          value={year}
          onChange={handleYearChange}
          fullWidth
          margin="normal"
          placeholder="2024"
          helperText="Enter the year of the expenses (e.g., 2024)"
          inputProps={{ maxLength: 4 }}
        />

        <Button
          component="label"
          variant="outlined"
          startIcon={<UploadIcon />}
          fullWidth
          sx={{ mt: 2, mb: 2 }}
          disabled={uploading}
        >
          {selectedFile ? selectedFile.name : 'Choose Excel File'}
          <input
            id="file-input"
            type="file"
            hidden
            accept=".xlsx,.xls"
            onChange={handleFileChange}
            disabled={uploading}
          />
        </Button>

        {selectedFile && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
          </Typography>
        )}

        {uploading && (
          <Box sx={{ mb: 2 }}>
            <LinearProgress variant="determinate" value={progress} />
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
              {progress}%
            </Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 2 }}>
          {onPreview && (
            <Button
              variant="outlined"
              onClick={handlePreview}
              disabled={!selectedFile || uploading}
              fullWidth
            >
              Preview
            </Button>
          )}
          
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            fullWidth
          >
            {uploading ? 'Uploading...' : 'Upload & Import'}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default FileUploader;
