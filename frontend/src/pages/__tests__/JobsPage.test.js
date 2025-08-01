import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import JobsPage from '../../pages/JobsPage';
import { BrowserRouter } from 'react-router-dom';
import { getAllJobs } from '../../services/api';

// Mock the API service
jest.mock('../../services/api', () => ({
  getAllJobs: jest.fn(),
}));

describe('JobsPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    // Setup the mock to return a promise that doesn't resolve immediately
    getAllJobs.mockImplementation(() => new Promise(() => {}));
    
    render(
      <BrowserRouter>
        <JobsPage />
      </BrowserRouter>
    );
    
    // Check for loading indicator
    expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument();
  });

  test('renders jobs when data is loaded', async () => {
    // Mock job data
    const mockJobs = [
      {
        job_id: '123e4567-e89b-12d3-a456-426614174000',
        status: 'COMPLETED',
        source_file: '/path/to/file1.csv',
        created_at: '2025-07-31T10:00:00',
        updated_at: '2025-07-31T10:05:00',
        output_file: '/path/to/output1.csv',
        error_message: null
      },
      {
        job_id: '223e4567-e89b-12d3-a456-426614174001',
        status: 'PROCESSING',
        source_file: '/path/to/file2.csv',
        created_at: '2025-08-01T09:00:00',
        updated_at: '2025-08-01T09:01:00',
        output_file: null,
        error_message: null
      }
    ];
    
    // Setup the mock to resolve with our test data
    getAllJobs.mockResolvedValue(mockJobs);
    
    render(
      <BrowserRouter>
        <JobsPage />
      </BrowserRouter>
    );
    
    // Wait for jobs to be displayed
    await waitFor(() => {
      expect(screen.getByText('file1.csv')).toBeInTheDocument();
      expect(screen.getByText('file2.csv')).toBeInTheDocument();
    });
    
    // Check status badges
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
    expect(screen.getByText('PROCESSING')).toBeInTheDocument();
  });

  test('renders error message when API call fails', async () => {
    // Setup the mock to reject with an error
    getAllJobs.mockRejectedValue({ message: 'Failed to fetch jobs' });
    
    render(
      <BrowserRouter>
        <JobsPage />
      </BrowserRouter>
    );
    
    // Wait for error message to be displayed
    await waitFor(() => {
      expect(screen.getByText('Failed to fetch jobs')).toBeInTheDocument();
    });
  });

  test('renders empty state when no jobs are found', async () => {
    // Setup the mock to resolve with an empty array
    getAllJobs.mockResolvedValue([]);
    
    render(
      <BrowserRouter>
        <JobsPage />
      </BrowserRouter>
    );
    
    // Wait for empty state message to be displayed
    await waitFor(() => {
      expect(screen.getByText(/No jobs found/i)).toBeInTheDocument();
    });
  });
});
