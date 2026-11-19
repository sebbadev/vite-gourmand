import { Routes } from '@angular/router';

import { Home } from './features/home/home';
import { Contact } from './features/contact/contact';
import { Legal } from './features/legal/legal';
import { Login } from './features/auth/login';
import { Register } from './features/auth/register';
import { ResetPassword } from './features/auth/reset-password';
import { CatalogueList } from './features/catalogue/catalogue-list';
import { MenuDetailPage } from './features/catalogue/menu-detail';
import { PanierPage } from './features/panier/panier';
import { ClientDashboard } from './features/client/client-dashboard';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';
import { EmployeDashboard } from './features/employe/employe-dashboard';
import { AdminDashboard } from './features/admin/admin-dashboard';

export const routes: Routes = [
  { path: '', component: Home, title: 'Vite & Gourmand — Traiteur Événementiel' },
  { path: 'catalogue', component: CatalogueList, title: 'Nos Menus — Vite & Gourmand' },
  { path: 'catalogue/:id', component: MenuDetailPage, title: 'Détail du Menu — Vite & Gourmand' },
  { path: 'panier', component: PanierPage, title: 'Panier & Devis — Vite & Gourmand' },
  { path: 'contact', component: Contact, title: 'Contact — Vite & Gourmand' },
  { path: 'mentions-legales', component: Legal, title: 'Mentions Légales & CGV — Vite & Gourmand' },
  { path: 'connexion', component: Login, title: 'Connexion — Vite & Gourmand' },
  { path: 'inscription', component: Register, title: 'Inscription — Vite & Gourmand' },
  { path: 'mot-de-passe-oublie', component: ResetPassword, title: 'Réinitialisation — Vite & Gourmand' },
  { path: 'mon-compte', component: ClientDashboard, canActivate: [authGuard], title: 'Mon Espace Client — Vite & Gourmand' },
  { path: 'employe', component: EmployeDashboard, canActivate: [roleGuard(['Employé', 'Administrateur'])], title: 'Gestion Traiteur — Vite & Gourmand' },
  { path: 'admin', component: AdminDashboard, canActivate: [roleGuard(['Administrateur'])], title: 'Administration & Statistiques — Vite & Gourmand' },
  { path: '**', redirectTo: '' }
];