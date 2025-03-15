'use client'

import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Upload, File, X, CheckCircle } from 'lucide-react'
import { useState, useEffect } from "react"
import { useToast } from "@/hooks/use-toast"
import { Label } from "@/components/ui/label"

type UploadedFile = {
  name: string
  size: number
  type: string
  file: File
}

export function DocumentUpload() {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [collectionName, setCollectionName] = useState('')
  const [description, setDescription] = useState('')
  const [address, setAddress] = useState('')
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const { toast } = useToast()

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    setShowSuccess(false)

    const droppedFiles = Array.from(e.dataTransfer.files).map(file => ({
      name: file.name,
      size: file.size,
      type: file.type,
      file: file
    }))
    setFiles(prev => [...prev, ...droppedFiles])
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setShowSuccess(false)
      const selectedFiles = Array.from(e.target.files).map(file => ({
        name: file.name,
        size: file.size,
        type: file.type,
        file: file
      }))
      setFiles(prev => [...prev, ...selectedFiles])
    }
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (files.length === 0 || !collectionName || !description) {
      toast({
        title: "Error",
        description: "Please provide a file, collection name, and description.",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)
    setShowSuccess(false)

    try {
      for (const file of files) {
        const formData = new FormData()
        formData.append('file', file.file)
        formData.append('collection_name', collectionName)
        formData.append('description', description)
        if (address) formData.append('address', address)
        if (latitude) formData.append('latitude', latitude)
        if (longitude) formData.append('longitude', longitude)

        const response = await fetch('http://127.0.0.1:5000/new_upload', {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error(`Upload failed for ${file.name}`)
        }

        const data = await response.json()
        toast({
          title: "Success",
          description: `${file.name} uploaded successfully`,
        })
      }

      // Clear files and show success message only after all files are uploaded
      setFiles([])
      setShowSuccess(true)

      // Hide success message after 3 seconds
      setTimeout(() => {
        setShowSuccess(false)
      }, 3000)

    } catch (error) {
      console.error('Error uploading:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to upload file",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-4">
        <h2 className="font-semibold">Upload Documents</h2>
        <p className="text-sm text-muted-foreground">
          Upload PDFs, images, audio, and video files to chat with
        </p>
      </div>

      <div className="flex-1 overflow-hidden">
        <div className="p-4 space-y-4 h-[calc(100%-80px)] overflow-auto">
          <div>
            <Label htmlFor="collection-name">Collection Name *</Label>
            <Input
              id="collection-name"
              type="text"
              placeholder="Collection Name"
              value={collectionName}
              onChange={(e) => setCollectionName(e.target.value)}
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              placeholder="File description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="address">Address</Label>
            <Input
              id="address"
              type="text"
              placeholder="Geographic location"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="mt-1"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="latitude">Latitude</Label>
              <Input
                id="latitude"
                type="number"
                placeholder="Latitude"
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="longitude">Longitude</Label>
              <Input
                id="longitude"
                type="number"
                placeholder="Longitude"
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>

          {showSuccess && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-2 text-green-600">
              <CheckCircle className="h-5 w-5" />
              <span>All files uploaded successfully!</span>
            </div>
          )}

          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 ease-in-out ${
              isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/20 hover:border-primary/50'
            }`}
            onDragOver={(e: React.DragEvent<HTMLDivElement>) => {
              e.preventDefault()
              setIsDragging(true)
            }}
            onDragLeave={(e: React.DragEvent<HTMLDivElement>) => {
              e.preventDefault()
              setIsDragging(false)
            }}
            onDrop={handleDrop}
          >
            <Upload className="w-8 h-8 mx-auto mb-4 text-muted-foreground" />
            <h3 className="font-medium mb-1">Drag and drop your files here</h3>
            <p className="text-sm text-muted-foreground mb-4">
              or click to browse from your computer
            </p>
            <Button
              variant="outline"
              onClick={() => document.getElementById('file-input')?.click()}
              className="transition-all duration-200 ease-in-out hover:bg-primary/10 active:scale-95"
            >
              Choose Files
            </Button>
            <input
              id="file-input"
              type="file"
              multiple
              className="hidden"
              onChange={handleFileInput}
            />
          </div>

          {files.length > 0 && (
            <div className="space-y-2">
              {files.map((file, i) => (
                <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                  <File className="w-4 h-4 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFile(i)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="border-t p-4 bg-background sticky bottom-0">
          <Button
            className="w-full transition-all duration-200 ease-in-out hover:bg-primary/90 active:scale-95"
            onClick={handleUpload}
            disabled={files.length === 0 || !collectionName || !description || isUploading}
          >
            {isUploading ? (
              <>
                <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                Uploading...
              </>
            ) : (
              'Upload Files'
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}

