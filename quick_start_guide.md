# AFSP Quick Start Guide

## Overview

The Automated Financial Statement Processor (AFSP) is a tool that helps you convert various financial documents into QuickBooks-compatible CSV files. This guide will help you get started quickly.

## Getting Started

1. Start the application by running:
   ```
   ./start_app.sh
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:3000
   ```

## Using the Application

### Uploading Files

1. Click on the "Upload" tab in the navigation menu.
2. Either drag and drop your financial document into the upload area or click to select a file.
3. Choose your preferred QuickBooks CSV format:
   - **3-Column**: Date, Description, Amount
   - **4-Column**: Date, Description, Debit, Credit
4. Select your preferred date format:
   - MM/DD/YYYY (US format)
   - DD/MM/YYYY (European format)
5. Click the "Upload Document" button.

Supported file types:
- CSV (comma-separated values files)
- PDF (bank statements or financial documents)
- DOCX (Word documents with financial data)
- JPEG/PNG (receipt images)

### Checking Job Status

1. After uploading, you'll be redirected to the job details page.
2. The status will initially show as "PROCESSING".
3. The page will automatically refresh until processing is complete.
4. Once complete, you'll see a preview of the extracted data.

### Downloading Results

1. When a job is completed, click the "Download QuickBooks CSV" button.
2. The CSV file will be downloaded to your computer.
3. You can now import this file into QuickBooks.

### Managing Jobs

1. Click on the "Jobs" tab to see all your processing jobs.
2. Click on any job to view its details and download results.
3. Use the pagination controls to navigate through multiple jobs.

### Customizing Settings

1. Click on the "Settings" tab to customize your preferences.
2. Change default CSV and date formats.
3. Adjust auto-refresh settings for job monitoring.
4. Click "Save Settings" to apply your changes.

## Troubleshooting

If you encounter any issues:

1. Check that both the backend and frontend services are running.
2. Ensure your file meets the requirements (supported format and under 10MB).
3. Try refreshing the job status page manually if auto-refresh isn't working.
4. For failed jobs, check the error message displayed on the job details page.

For further assistance, please refer to the main documentation.
