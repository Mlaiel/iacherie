/// <reference types="vite/client" />

// Déclaration de module pour react-map-gl/mapbox
declare module 'react-map-gl/mapbox' {
  import { ComponentType, CSSProperties, ReactNode } from 'react';

  export interface ViewState {
    longitude: number;
    latitude: number;
    zoom: number;
    pitch?: number;
    bearing?: number;
  }

  export interface MapProps {
    mapStyle?: string;
    mapboxAccessToken?: string;
    style?: CSSProperties;
    onMove?: (evt: { viewState: ViewState }) => void;
    longitude?: number;
    latitude?: number;
    zoom?: number;
    children?: ReactNode;
    ref?: any;
  }

  export interface MarkerProps {
    longitude: number;
    latitude: number;
    anchor?: string;
    onClick?: (e: any) => void;
    children?: ReactNode;
  }

  export interface PopupProps {
    longitude: number;
    latitude: number;
    anchor?: string;
    onClose?: () => void;
    closeButton?: boolean;
    closeOnClick?: boolean;
    children?: ReactNode;
  }

  export interface NavigationControlProps {
    position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  }

  export interface GeolocateControlProps {
    position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  }

  const Map: ComponentType<MapProps>;
  export default Map;
  export const Marker: ComponentType<MarkerProps>;
  export const Popup: ComponentType<PopupProps>;
  export const NavigationControl: ComponentType<NavigationControlProps>;
  export const GeolocateControl: ComponentType<GeolocateControlProps>;
}
