import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileUpload from './FileUpload';
import { BrowserRouter } from 'react-router-dom';

// Mock the API service
jest.mock('../../services/api', () => ({
  uploadFile: jest.fn(),
}));

// Mock navigate from react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('FileUpload Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders file upload area', () => {
    render(
      <BrowserRouter>
        <FileUpload />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/Upload a file/i)).toBeInTheDocument();
    expect(screen.getByText(/or drag and drop/i)).toBeInTheDocument();
  });

  test('displays format options', () => {
    render(
      <BrowserRouter>
        <FileUpload />
      </BrowserRouter>
    );
    
    expect(screen.getByLabelText(/QuickBooks CSV Format/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Date Format/i)).toBeInTheDocument();
  });

  test('upload button is disabled when no file is selected', () => {
    render(
      <BrowserRouter>
        <FileUpload />
      </BrowserRouter>
    );
    
    const uploadButton = screen.getByRole('button', { name: /Upload Document/i });
    expect(uploadButton).toBeDisabled();
  });

  test('shows error for unsupported file type', async () => {
    const { container } = render(
      <BrowserRouter>
        <FileUpload />
      </BrowserRouter>
    );
    
    // Create a mock file with unsupported extension
    const file = new File(['file content'], 'test.exe', { type: 'application/octet-stream' });
    
    // Get the hidden file input
    const fileInput = container.querySelector('input[type="file"]');
    
    // Simulate file selection
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    // Check for error message
    expect(await screen.findByText(/Invalid file type/i)).toBeInTheDocument();
  });
});
