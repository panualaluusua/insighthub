# InsightHub Frontend

A modern content feed application built with SvelteKit, TypeScript, and TailwindCSS.

## Features

- 🚀 SvelteKit with TypeScript for type safety
- 🎨 TailwindCSS with custom design system
- 📱 Progressive Web App (PWA) support
- 🔐 Supabase authentication integration
- ⚡ Real-time content updates
- 🧪 Testing with Vitest and Playwright
- 📊 Performance optimized for content feeds

## Development Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Environment Configuration:**
   Create a `.env` file in the project root:
   ```env
   PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Run tests:**
   ```bash
   # Unit tests
   npm run test
   
   # E2E tests
   npm run test:e2e
   ```

5. **Build for production:**
   ```bash
   npm run build
   npm run preview
   ```

## Project Structure

```
src/
├── lib/                 # Shared utilities and components
├── routes/             # SvelteKit routes
├── app.css            # Global styles with TailwindCSS
├── app.html           # HTML template
└── app.d.ts           # TypeScript declarations
```

## Performance Targets

- Bundle size: < 50KB (currently ~46KB)
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Mobile-first responsive design

## Built With

- [SvelteKit](https://kit.svelte.dev/) - Web framework
- [TypeScript](https://www.typescriptlang.org/) - Type safety
- [TailwindCSS](https://tailwindcss.com/) - Styling
- [Supabase](https://supabase.io/) - Backend & Auth
- [Vite](https://vitejs.dev/) - Build tool
- [Vitest](https://vitest.dev/) - Unit testing
- [Playwright](https://playwright.dev/) - E2E testing
