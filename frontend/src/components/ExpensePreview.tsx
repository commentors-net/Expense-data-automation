/**
 * Component to preview normalized expense data before import
 */
import React from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
} from '@mui/material';
import type { ExpenseData } from '../api/expenses';

interface ExpensePreviewProps {
  data: ExpenseData[];
  filename?: string;
  totalRows?: number;
}

const ExpensePreview: React.FC<ExpensePreviewProps> = ({ data, filename, totalRows }) => {
  if (!data || data.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="body1" color="text.secondary">
          No preview data available
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box sx={{ mb: 2 }}>
        <Typography variant="h5" gutterBottom>
          Data Preview
        </Typography>
        {filename && (
          <Typography variant="body2" color="text.secondary">
            File: {filename}
          </Typography>
        )}
        {totalRows && (
          <Typography variant="body2" color="text.secondary">
            Showing {data.length} of {totalRows} rows
          </Typography>
        )}
      </Box>

      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell><strong>Date</strong></TableCell>
              <TableCell><strong>Category</strong></TableCell>
              <TableCell><strong>Description</strong></TableCell>
              <TableCell align="right"><strong>Amount</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((expense, index) => (
              <TableRow key={index} hover>
                <TableCell>{expense.date}</TableCell>
                <TableCell>
                  <Chip 
                    label={expense.category} 
                    size="small" 
                    color="primary" 
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>{expense.description}</TableCell>
                <TableCell align="right">
                  ${expense.amount.toFixed(2)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default ExpensePreview;
