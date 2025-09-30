'use client';

import { Fragment } from 'react';
import { Listbox, Transition } from '@headlessui/react';
import { ChevronUpDownIcon, CheckIcon, GlobeAltIcon } from '@heroicons/react/24/outline';
import { useLanguage } from '../../hooks/useLanguage';
import { clsx } from 'clsx';

export function LanguageSelector() {
  const { language, setLanguage, availableLanguages } = useLanguage();

  const currentLanguage = availableLanguages.find(lang => lang.code === language);

  return (
    <div className="relative">
      <Listbox value={language} onChange={setLanguage}>
        <div className="relative">
          <Listbox.Button className="relative flex items-center space-x-2 rounded-lg bg-white py-2 pl-3 pr-10 text-left shadow-sm ring-1 ring-gray-300 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 sm:text-sm cursor-pointer hover:bg-gray-50">
            <GlobeAltIcon className="h-5 w-5 text-gray-400" />
            <span className="block truncate font-medium text-gray-900">
              {currentLanguage?.nativeName || 'Language'}
            </span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronUpDownIcon
                className="h-5 w-5 text-gray-400"
                aria-hidden="true"
              />
            </span>
          </Listbox.Button>

          <Transition
            as={Fragment}
            leave="transition ease-in duration-100"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <Listbox.Options className="absolute right-0 z-10 mt-1 max-h-60 w-64 overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
              {availableLanguages.map((lang) => (
                <Listbox.Option
                  key={lang.code}
                  className={({ active }) =>
                    clsx(
                      'relative cursor-default select-none py-2 pl-10 pr-4',
                      active ? 'bg-primary-100 text-primary-900' : 'text-gray-900'
                    )
                  }
                  value={lang.code}
                >
                  {({ selected, active }) => (
                    <>
                      <div className="flex items-center justify-between">
                        <div>
                          <span
                            className={clsx(
                              'block font-medium',
                              selected ? 'text-primary-600' : ''
                            )}
                          >
                            {lang.nativeName}
                          </span>
                          <span
                            className={clsx(
                              'block text-xs',
                              selected ? 'text-primary-500' : 'text-gray-500'
                            )}
                          >
                            {lang.name}
                          </span>
                        </div>
                        <span className="text-xs text-gray-400 uppercase">
                          {lang.code}
                        </span>
                      </div>
                      {selected ? (
                        <span
                          className={clsx(
                            'absolute inset-y-0 left-0 flex items-center pl-3',
                            active ? 'text-primary-600' : 'text-primary-600'
                          )}
                        >
                          <CheckIcon className="h-5 w-5" aria-hidden="true" />
                        </span>
                      ) : null}
                    </>
                  )}
                </Listbox.Option>
              ))}
            </Listbox.Options>
          </Transition>
        </div>
      </Listbox>
    </div>
  );
}