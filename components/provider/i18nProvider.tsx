'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { NextIntlClientProvider } from 'next-intl';
import { Loading } from '../loading';

type I18nContextType = {
  locale: string;
  setLocale: (locale: string) => void;
};

const I18nContext = createContext<I18nContextType>({
  locale: 'vi',
  setLocale: () => { },
});

export const useI18n = () => useContext(I18nContext);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState('vi');
  const [messages, setMessages] = useState<any>({});
  const [isLoading, setIsLoading] = useState(true);

  // Load ngôn ngữ đã lưu
  useEffect(() => {
    const savedLocale = localStorage.getItem('locale') || 'vi';
    loadMessages(savedLocale);
  }, []);

  const loadMessages = async (newLocale: string) => {
    try {
      setIsLoading(true);
      const mod = await import(`@/locales/${newLocale}/common.json`);
      // console.log('Loaded messages for', newLocale, ':', mod.default); // Debug log
      setMessages(mod.default);
      setLocale(newLocale);
    } catch (error) {
      // console.error('Error loading messages:', error);
      // Fallback to empty object
      setMessages({});
    } finally {
      setIsLoading(false);
    }
  };

  const changeLocale = (newLocale: string) => {
    localStorage.setItem('locale', newLocale);
    loadMessages(newLocale);
  };

  // Show loading spinner until messages are loaded
  if (isLoading) {
    return (
      <Loading/>
    );
  }


  return (
    <I18nContext.Provider value={{ locale, setLocale: changeLocale }}>
      <NextIntlClientProvider
        locale={locale}
        messages={messages}
        timeZone="Asia/Ho_Chi_Minh"
      >
        {children}
      </NextIntlClientProvider>
    </I18nContext.Provider>
  );
}
