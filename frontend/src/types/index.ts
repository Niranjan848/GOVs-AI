/* ── Core Types ─────────────────────────────────────────────── */

export interface User {
  id: number;
  email: string;
  role: 'citizen' | 'admin';
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Profile {
  id: number;
  user_id: number;
  name: string;
  age: number | null;
  gender: string | null;
  state: string | null;
  district: string | null;
  occupation: string | null;
  annual_income: number | null;
  category: string | null;
  education: string | null;
  land_area_acres: number | null;
  has_disability: boolean;
  family_size: number | null;
  marital_status: string | null;
  has_bank_account: boolean;
  has_aadhaar: boolean;
  bpl_card: boolean;
  completion_percentage: number;
}

export interface ProfileCompletion {
  completion: number;
  missing_fields: string[];
  total_fields: number;
  filled_fields: number;
}

export interface Chat {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  messages: Message[];
}

export interface ChatListItem {
  id: number;
  title: string;
  created_at: string;
  message_count: number;
  last_message_preview: string;
}

export interface Message {
  id: number;
  chat_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata_json: MessageMetadata | null;
  created_at: string;
}

export interface MessageMetadata {
  schemes?: SchemePreview[] | null;
  checklist?: Checklist | null;
  intent?: string | null;
}

export interface SchemePreview {
  id: number | null;
  name: string;
  category: string;
  benefits_amount: string;
  score: number;
  reasoning: string;
}

export interface Scheme {
  id: number;
  name: string;
  short_name: string | null;
  category: string;
  description: string;
  eligibility: Record<string, unknown>;
  benefits: string;
  benefits_amount: string | null;
  documents_required: string[];
  application_process: string | null;
  website_url: string | null;
  ministry: string | null;
  state: string;
  is_active: boolean;
}

export interface Recommendation {
  id: number;
  scheme: Scheme;
  score: number;
  reasoning: string | null;
  checklist: Checklist | null;
  created_at: string;
}

export interface Bookmark {
  id: number;
  scheme: Scheme;
  created_at: string;
}

export interface Checklist {
  scheme_name: string;
  total_documents: number;
  items: ChecklistItem[];
  application_process: string;
  website_url: string;
}

export interface ChecklistItem {
  document: string;
  mandatory: boolean;
  user_likely_has: boolean;
  tips: string;
}

export interface Notification {
  id: number;
  title: string;
  body: string;
  notification_type: 'info' | 'recommendation' | 'update' | 'alert';
  read: boolean;
  created_at: string;
}

export interface AdminStats {
  total_users: number;
  total_chats: number;
  total_schemes: number;
  total_documents: number;
  total_recommendations: number;
  popular_schemes: { name: string; count: number }[];
  popular_states: { state: string; count: number }[];
  recent_signups: number;
}

/* ── Demo Users for Login ──────────────────────────────────── */
export interface DemoUser {
  email: string;
  password: string;
  name: string;
  role: string;
  avatar: string;
  description: string;
}

export const DEMO_USERS: DemoUser[] = [
  {
    email: 'ramesh@demo.govsai.in',
    password: 'demo123',
    name: 'Ramesh Kumar',
    role: 'Farmer',
    avatar: '🌾',
    description: '45y, UP, ₹1.2L income, 3 acres land',
  },
  {
    email: 'priya@demo.govsai.in',
    password: 'demo123',
    name: 'Priya Sharma',
    role: 'Student',
    avatar: '📚',
    description: '20y, Maharashtra, SC category, Undergraduate',
  },
  {
    email: 'sunita@demo.govsai.in',
    password: 'demo123',
    name: 'Sunita Devi',
    role: 'Woman Entrepreneur',
    avatar: '👩‍💼',
    description: '35y, Gujarat, Business owner, Graduate',
  },
  {
    email: 'mohan@demo.govsai.in',
    password: 'demo123',
    name: 'Mohan Pillai',
    role: 'Senior Citizen',
    avatar: '🧓',
    description: '68y, Tamil Nadu, Retired, Pension needed',
  },
  {
    email: 'vikram@demo.govsai.in',
    password: 'demo123',
    name: 'Vikram Reddy',
    role: 'Startup Founder',
    avatar: '🚀',
    description: '30y, Karnataka, Tech startup, PG',
  },
];

/* ── Scheme Categories ─────────────────────────────────────── */
export const SCHEME_CATEGORIES = [
  { id: 'all', label: 'All Schemes', icon: '📋' },
  { id: 'agriculture', label: 'Agriculture', icon: '🌾' },
  { id: 'education', label: 'Education', icon: '📚' },
  { id: 'health', label: 'Health', icon: '🏥' },
  { id: 'business', label: 'Business', icon: '💼' },
  { id: 'women', label: 'Women', icon: '👩' },
  { id: 'pension', label: 'Pension', icon: '🏦' },
  { id: 'housing', label: 'Housing', icon: '🏠' },
  { id: 'skill', label: 'Skill Development', icon: '🔧' },
];

/* ── Indian States ─────────────────────────────────────────── */
export const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
  'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
  'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
  'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Delhi', 'Jammu & Kashmir', 'Ladakh',
];
