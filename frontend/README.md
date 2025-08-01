# AFSP Frontend

This is the frontend application for the Automated Financial Statement Processor (AFSP) system. It provides a user-friendly interface for uploading financial documents, tracking processing jobs, and downloading QuickBooks-compatible CSV files.

## Features

- Modern React-based UI with Tailwind CSS for styling
- Responsive design that works on desktop and mobile devices
- Drag-and-drop file upload with validation
- Real-time job status monitoring
- QuickBooks CSV format options
- Accessible UI with keyboard navigation support

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- AFSP backend server running

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```
   cd frontend
   ```
3. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

### Running the Application

Start the development server:

```
npm start
```

or

```
yarn start
```

The application will be available at [http://localhost:3000](http://localhost:3000).

## Project Structure

- `/src/components` - Reusable UI components
- `/src/pages` - Page components that represent different routes
- `/src/services` - API client and other service functions
- `/src/context` - React context providers for state management

## Backend Communication

The frontend communicates with the AFSP backend API running at `http://localhost:8000`. The proxy is configured in `package.json` to forward API requests during development.

## Building for Production

To create an optimized production build:

```
npm run build
```

or

```
yarn build
```

The build artifacts will be stored in the `build` directory.

## Accessibility

This application is designed with accessibility in mind, following WCAG guidelines. Key features include:

- Keyboard navigation
- Screen reader compatibility
- Proper ARIA attributes
- Sufficient color contrast

## License

This project is proprietary and confidential.

---

For more information, please refer to the main project documentation.
