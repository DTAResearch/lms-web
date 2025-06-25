// lib/i18nProvider.tsx
'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { NextIntlClientProvider } from 'next-intl';

type I18nContextType = {
  locale: string;
  setLocale: (locale: string) => void;
};

const I18nContext = createContext<I18nContextType>({
  locale: 'vi',
  setLocale: () => {},
});

export const useI18n = () => useContext(I18nContext);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState('vi');
  const [messages, setMessages] = useState<any>({});

  // Load ngôn ngữ đã lưu
  useEffect(() => {
    const savedLocale = localStorage.getItem('locale') || 'vi';
    loadMessages(savedLocale);
  }, []);

  const loadMessages = async (newLocale: string) => {
    // const mod = await import(`../locales/${newLocale}/common.json`);
    const mod = await import(`@/locales/${newLocale}/common.json`);
    setMessages(mod.default);
    setLocale(newLocale);
  };

  const changeLocale = (newLocale: string) => {
    localStorage.setItem('locale', newLocale);
    loadMessages(newLocale);
  };

  return (
    <I18nContext.Provider value={{ locale, setLocale: changeLocale }}>
      <NextIntlClientProvider locale={locale} messages={messages}>
        {children}
      </NextIntlClientProvider>
    </I18nContext.Provider>
  );
}
