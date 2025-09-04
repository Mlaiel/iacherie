import { useState, useEffect } from 'react';

interface BatteryState {
  charging: boolean;
  chargingTime: number;
  dischargingTime: number;
  level: number;
}

export const useBattery = () => {
  const [battery, setBattery] = useState<BatteryState | null>(null);

  useEffect(() => {
    let batteryRef: any = null;

    const updateBattery = (battery: any) => {
      setBattery({
        charging: battery.charging,
        chargingTime: battery.chargingTime,
        dischargingTime: battery.dischargingTime,
        level: battery.level,
      });
    };

    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        batteryRef = battery;
        updateBattery(battery);

        battery.addEventListener('chargingchange', () => updateBattery(battery));
        battery.addEventListener('levelchange', () => updateBattery(battery));
      });
    }

    return () => {
      if (batteryRef) {
        batteryRef.removeEventListener('chargingchange', updateBattery);
        batteryRef.removeEventListener('levelchange', updateBattery);
      }
    };
  }, []);

  return battery;
};
