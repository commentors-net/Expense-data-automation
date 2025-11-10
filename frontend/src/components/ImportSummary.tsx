/**
 * Component to display import summary statistics
 */
import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface ImportSummaryProps {
  imported: number;
  skipped: number;
  status: string;
  message?: string;
}

const ImportSummary: React.FC<ImportSummaryProps> = ({
  imported,
  skipped,
  status,
  message,
}) => {
  const isSuccess = status === 'ok' && imported > 0;

  return (
    <Card elevation={3}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {isSuccess ? (
            <SuccessIcon color="success" sx={{ mr: 1, fontSize: 32 }} />
          ) : (
            <ErrorIcon color="error" sx={{ mr: 1, fontSize: 32 }} />
          )}
          <Typography variant="h5">
            {isSuccess ? 'Import Successful' : 'Import Failed'}
          </Typography>
        </Box>

        <Divider sx={{ mb: 2 }} />

        <Box sx={{ display: 'flex', gap: 3, justifyContent: 'space-around', flexWrap: 'wrap' }}>
          <Box sx={{ textAlign: 'center', flex: 1, minWidth: 150 }}>
            <Typography variant="h3" color="success.main">
              {imported}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Records Imported
            </Typography>
          </Box>
          
          {skipped > 0 && (
            <Box sx={{ textAlign: 'center', flex: 1, minWidth: 150 }}>
              <Typography variant="h3" color="warning.main">
                {skipped}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Records Skipped
              </Typography>
            </Box>
          )}
        </Box>

        {message && (
          <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
            <InfoIcon color="info" sx={{ mr: 1 }} />
            <Typography variant="body2" color="text.secondary">
              {message}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ImportSummary;
