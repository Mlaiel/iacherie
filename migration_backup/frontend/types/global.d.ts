import React from 'react'

declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any
    }
  }
}

declare module NodeJS {
  interface ProcessEnv {
    NODE_ENV: 'development' | 'production' | 'test'
    NEXT_PUBLIC_API_URL?: string
    [key: string]: string | undefined
  }
}

// Next.js types
declare module 'next/router' {
  import { NextRouter } from 'next/dist/client/router'
  export { NextRouter }
  export default NextRouter
}

declare module 'next/link' {
  import { ComponentProps } from 'react'
  interface LinkProps {
    href: string
    as?: string
    replace?: boolean
    scroll?: boolean
    shallow?: boolean
    passHref?: boolean
    prefetch?: boolean
    locale?: string | false
    className?: string
    children?: React.ReactNode
  }
  export default function Link(props: LinkProps): JSX.Element
}

declare module 'next/server' {
  export interface NextRequest extends Request {
    nextUrl: {
      pathname: string
      search: string
      searchParams: URLSearchParams
    }
    ip?: string
    geo?: {
      country?: string
      region?: string
      city?: string
      latitude?: string
      longitude?: string
    }
  }

  export class NextResponse extends Response {
    static json(object: any, init?: ResponseInit): NextResponse
    static redirect(url: string | URL, init?: ResponseInit): NextResponse
    static rewrite(destination: string | URL, init?: ResponseInit): NextResponse
    static next(init?: ResponseInit): NextResponse
  }
}

// React types
declare module 'react' {
  interface HTMLAttributes<T> extends AriaAttributes, DOMAttributes<T> {
    className?: string
    [key: string]: any
  }
}

export {}