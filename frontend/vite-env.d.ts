/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly PROD: boolean;
  readonly DEV: boolean;
  // more env variables...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}