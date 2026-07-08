import { useState, useRef, useCallback } from 'react'

// Types
interface AnalysisResult {
  success: boolean
  content: string | object | null
  model?: string
  pages_processed?: number
  usage?: {
    prompt_tokens?: number
    completion_tokens?: number
    total_tokens?: number
  }
  error?: string
}

interface UploadState {
  status: 'idle' | 'uploading' | 'analyzing' | 'success' | 'error'
  message: string
  result?: AnalysisResult
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function MedicalDocumentUploader() {
  const [uploadState, setUploadState] = useState<UploadState>({ status: 'idle', message: '' })
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [dragActive, setDragActive] = useState(false)
  const [customPrompt, setCustomPrompt] = useState('')

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        setSelectedFile(file)
      } else {
        setUploadState({ status: 'error', message: 'Only PDF files are supported' })
      }
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        setSelectedFile(file)
      } else {
        setUploadState({ status: 'error', message: 'Only PDF files are supported' })
      }
    }
  }

  const validateFile = (file: File): string | null => {
    const maxSize = 20 * 1024 * 1024 // 20MB
    if (file.size > maxSize) {
      return 'File size must be less than 20MB'
    }
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return 'Only PDF files are supported'
    }
    return null
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    const validationError = validateFile(selectedFile)
    if (validationError) {
      setUploadState({ status: 'error', message: validationError })
      return
    }

    setUploadState({ status: 'uploading', message: 'Uploading PDF...' })

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      if (customPrompt.trim()) {
        formData.append('prompt', customPrompt.trim())
      }

      // Upload to backend
      const uploadResponse = await fetch(`${API_URL}/api/analyze-medical-document`, {
        method: 'POST',
        body: formData,
      })

      setUploadState({ status: 'analyzing', message: 'Analyzing with Fireworks AI...' })

      const result: AnalysisResult = await uploadResponse.json()

      if (!uploadResponse.ok || !result.success) {
        throw new Error(result.error || 'Analysis failed')
      }

      setUploadState({ 
        status: 'success', 
        message: `Analysis complete! ${result.pages_processed} page(s) processed.`,
        result 
      })
    } catch (error) {
      setUploadState({ 
        status: 'error', 
        message: error instanceof Error ? error.message : 'An error occurred' 
      })
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setCustomPrompt('')
    setUploadState({ status: 'idle', message: '' })
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const getStatusColor = () => {
    switch (uploadState.status) {
      case 'success': return 'text-green-700 bg-green-50 border-green-200'
      case 'error': return 'text-red-700 bg-red-50 border-red-200'
      case 'analyzing': return 'text-blue-700 bg-blue-50 border-blue-200'
      case 'uploading': return 'text-amber-700 bg-amber-50 border-amber-200'
      default: return 'text-gray-700 bg-gray-50 border-gray-200'
    }
  }

  const formatContent = (content: string | object | null) => {
    if (!content) return 'No content'
    if (typeof content === 'string') return content
    return JSON.stringify(content, null, 2)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">BrainConnect</h1>
          <p className="text-lg text-gray-600">Medical Document Analysis with Fireworks AI</p>
          <p className="mt-2 text-sm text-gray-500">Powered by Vision Language Models</p>
        </div>

        {/* Upload Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Upload Zone */}
          <div
            className={`border-2 border-dashed rounded-t-xl p-8 transition-all ${
              dragActive 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              id="file-upload"
              className="hidden"
              accept=".pdf"
              onChange={handleFileSelect}
            />

            <div className="text-center">
              <svg
                className="mx-auto h-14 w-14 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p className="mt-3 text-lg text-gray-600">
                {selectedFile 
                  ? `Selected: ${selectedFile.name} (${(selectedFile.size / 1024 / 1024).toFixed(2)} MB)`
                  : 'Drag & drop a medical PDF, or click to browse'}
              </p>
              <p className="mt-1 text-sm text-gray-500">
                PDF only • Max 20MB • Medical records, radiology reports, lab results
              </p>
              
              {!selectedFile && (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="mt-4 inline-flex items-center px-5 py-2.5 border border-transparent text-base font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                  </svg>
                  Choose PDF File
                </button>
              )}
            </div>
          </div>

          {/* Selected File Info */}
          {selectedFile && (
            <div className="px-8 py-4 border-t border-gray-100 bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <svg className="h-7 w-7 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB • PDF</p>
                  </div>
                </div>
                <button
                  onClick={handleReset}
                  className="text-sm text-red-600 hover:text-red-800 font-medium px-3 py-1 rounded border border-red-200 hover:bg-red-50"
                >
                  Remove
                </button>
              </div>
            </div>
          )}

          {/* Custom Prompt Section */}
          <div className="px-8 py-6 border-t border-gray-100">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Custom Analysis Prompt (Optional)
            </label>
            <p className="text-sm text-gray-500 mb-3">
              Leave blank to use default medical extraction prompt. Customize for specific analysis needs.
            </p>
            <textarea
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm font-mono resize-y"
              placeholder="e.g., Focus on cardiac findings and medication changes..."
            />
          </div>

          {/* Action Buttons */}
          <div className="px-8 py-6 border-t border-gray-100 bg-gray-50 flex justify-center gap-4">
            {selectedFile && uploadState.status !== 'uploading' && uploadState.status !== 'analyzing' && (
              <button
                onClick={handleUpload}
                disabled={uploadState.status === 'uploading' || uploadState.status === 'analyzing'}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Analyze with Fireworks AI
              </button>
            )}
            
            {uploadState.status === 'success' && (
              <button
                onClick={handleReset}
                className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50"
              >
                <svg className="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Analyze Another
              </button>
            )}
          </div>

          {/* Status Display */}
          {uploadState.status !== 'idle' && (
            <div className={`mx-8 my-4 p-4 rounded-lg border ${getStatusColor()}`}>
              <div className="flex items-center">
                {uploadState.status === 'uploading' && (
                  <svg className="animate-spin h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                )}
                {uploadState.status === 'analyzing' && (
                  <svg className="animate-spin h-6 w-6 mr-3 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                )}
                {uploadState.status === 'success' && (
                  <svg className="h-6 w-6 mr-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                {uploadState.status === 'error' && (
                  <svg className="h-6 w-6 mr-3 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                )}
                <p className="font-medium">{uploadState.message}</p>
              </div>
            </div>
          )}

          {/* Result Display */}
          {uploadState.result && uploadState.status === 'success' && (
            <div className="mx-8 mb-8 p-6 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Analysis Result</h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => navigator.clipboard.writeText(formatContent(uploadState.result?.content))}
                    className="text-sm text-indigo-600 hover:text-indigo-800 px-3 py-1 rounded border border-indigo-200 bg-white"
                  >
                    Copy Result
                  </button>
                  <button
                    onClick={() => {
                      const blob = new Blob([formatContent(uploadState.result?.content)], { type: 'application/json' })
                      const url = URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = 'brainconnect-analysis.json'
                      a.click()
                      URL.revokeObjectURL(url)
                    }}
                    className="text-sm text-indigo-600 hover:text-indigo-800 px-3 py-1 rounded border border-indigo-200 bg-white"
                  >
                    Download JSON
                  </button>
                </div>
              </div>
              <div className="bg-white p-4 rounded border border-gray-200 max-h-96 overflow-y-auto font-mono text-sm text-gray-800 whitespace-pre-wrap break-words">
                {formatContent(uploadState.result.content)}
              </div>
              
              {/* Metadata */}
              {uploadState.result.pages_processed && (
                <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-3 gap-4 text-sm">
                  <div className="text-center">
                    <p className="font-semibold text-gray-900">{uploadState.result.pages_processed}</p>
                    <p className="text-gray-500">Pages Processed</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold text-gray-900">{uploadState.result.model || 'N/A'}</p>
                    <p className="text-gray-500">Model Used</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold text-gray-900">
                      {uploadState.result.usage?.total_tokens ? uploadState.result.usage.total_tokens.toLocaleString() : 'N/A'}
                    </p>
                    <p className="text-gray-500">Total Tokens</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Info Card */}
        <div className="mt-8 p-6 bg-indigo-50 rounded-xl border border-indigo-100">
          <h3 className="text-lg font-medium text-indigo-800 mb-3">How it works</h3>
          <ul className="text-sm text-indigo-700 space-y-2">
            <li className="flex items-start"><svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0 text-indigo-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>Upload a medical PDF (patient history, radiology report, lab results, discharge summary)</li>
            <li className="flex items-start"><svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0 text-indigo-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>PDF pages are converted to images and sent to Fireworks Vision Language Model (kimi-k2p5)</li>
            <li className="flex items-start"><svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0 text-indigo-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>AI extracts structured clinical data: demographics, complaints, history, labs, imaging, assessment, plan</li>
            <li className="flex items-start"><svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0 text-indigo-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>Results returned as structured JSON for integration into BrainConnect multi-agent pipeline</li>
          </ul>
          <p className="mt-4 text-sm text-indigo-600">
            <strong>Backend:</strong> FastAPI + Fireworks AI | <strong>Frontend:</strong> React + Vite + Tailwind
          </p>
        </div>
      </div>
    </div>
  )
}