import { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  message: string
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: '' }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Render error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="bg-white border rounded-xl p-8 max-w-md text-center">
            <h1 className="text-lg font-semibold mb-2">Something went wrong</h1>
            <p className="text-sm text-gray-500 mb-4">{this.state.message}</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 text-white rounded-lg px-4 py-2 text-sm"
            >
              Reload
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
