declare global {
  interface Window {
    desktop?: {
      platform: string;
      version: string;
    };
  }
}

export {};
