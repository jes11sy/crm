// Тип пользователя
export interface User {
  id: number;
  name: string;
  role: string;
  gorod_id?: number;
}

// Тип города
export interface Gorod {
  id: number;
  name: string;
}

// Тип опции для select
export interface Option {
  value: string | number;
  label: string;
}

// Тип транзакции
export interface Tranzakciya {
  id: number;
  gorod: number | string;
  gorod_name?: string;
  tip_tranzakcii: number | string;
  tip_tranzakcii_name?: string;
  summa: number;
  date: string;
  note?: string;
}

// Тип типа транзакции
export interface TipTranzakcii {
  id: number;
  name: string;
}

// Тип телефона города
export interface PhoneGoroda {
  id: number;
  gorod: number | Gorod;
  phone: string;
} 