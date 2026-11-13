import { Routes } from '@angular/router';

import { Home } from './features/home/home';
import { Contact } from './features/contact/contact';

export const routes: Routes = [
  { path: '', component: Home, title: 'Vite & Gourmand — Traiteur Événementiel' },
  { path: 'contact', component: Contact, title: 'Contact — Vite & Gourmand' },
  { path: '**', redirectTo: '' }
];