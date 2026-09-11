import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AppStateProvider } from './context/AppStateContext';
import { AppRoutes } from './routes';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AppStateProvider>
          <AppRoutes />
        </AppStateProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

export default App;
