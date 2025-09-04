import { useState, useCallback } from 'react';

type ValidationRule<T> = (value: T) => string | null;

export const useValidation = <T>(initialValue: T, rules: ValidationRule<T>[] = []) => {
  const [value, setValue] = useState<T>(initialValue);
  const [error, setError] = useState<string | null>(null);
  const [touched, setTouched] = useState(false);

  const validate = useCallback((newValue: T) => {
    for (const rule of rules) {
      const error = rule(newValue);
      if (error) {
        setError(error);
        return false;
      }
    }
    setError(null);
    return true;
  }, [rules]);

  const handleChange = useCallback((newValue: T) => {
    setValue(newValue);
    if (touched) validate(newValue);
  }, [touched, validate]);

  const handleBlur = useCallback(() => {
    setTouched(true);
    validate(value);
  }, [value, validate]);

  return { value, error, touched, handleChange, handleBlur, validate };
};
