# Menu Engineer

AI-powered menu optimization tool for restaurants.

## Project Structure

```
menu-engineer/
├── src/
│   ├── components/
│   │   ├── ChangeCard.tsx          # Individual change recommendation card
│   │   ├── FileUpload.tsx          # File upload component with drag & drop
│   │   ├── LoadingSpinner.tsx      # Loading state component
│   │   ├── ResultsDisplay.tsx      # Results container component
│   │   └── SummaryCard.tsx         # Summary statistics card
│   ├── types/
│   │   └── menu.types.ts           # TypeScript type definitions
│   ├── utils/
│   │   ├── api.ts                  # API service for backend communication
│   │   └── helpers.ts              # Utility helper functions
│   ├── styles/
│   │   └── global.css              # Global styles
│   ├── MenuAnalyzer.tsx            # Main component orchestrator
│   └── main.tsx                    # Application entry point
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

## Component Breakdown

### Core Components

- **MenuAnalyzer.tsx**: Main container that manages state and orchestrates child components
- **FileUpload.tsx**: Handles file selection via click or drag & drop
- **LoadingSpinner.tsx**: Shows loading state during analysis
- **ResultsDisplay.tsx**: Displays analysis results with summary and changes
- **SummaryCard.tsx**: Reusable card for summary statistics
- **ChangeCard.tsx**: Displays individual menu change recommendations

### Utilities

- **api.ts**: Contains the API service layer for backend communication (currently mocked)
- **helpers.ts**: UI helper functions (icon mapping, class generation)
- **menu.types.ts**: All TypeScript type definitions

## Setup Instructions

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

4. **Preview production build:**
   ```bash
   npm run preview
   ```