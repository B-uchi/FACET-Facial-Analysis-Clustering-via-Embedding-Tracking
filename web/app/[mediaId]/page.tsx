"use client";

import { useState, useRef, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { ChevronLeft, Search, Upload, Loader2, CheckCircle2, AlertCircle, Play } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function MediaDetailPage() {
  const { mediaId } = useParams();
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [searching, setSearching] = useState(false);
  const [result, setResult] = useState<{ found: boolean; timestamp?: number; distance?: number; reason?: string } | null>(null);
  const [mediaInfo, setMediaInfo] = useState<{ id: string; url: string } | null>(null);

  useEffect(() => {
    fetchMediaInfo();
  }, [mediaId]);

  const fetchMediaInfo = async () => {
    try {
      const res = await axios.get(`${API_URL}/media/${mediaId}`);
      setMediaInfo(res.data);
    } catch (err) {
      console.error("Failed to fetch media info", err);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setSearching(true);
    setResult(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${API_URL}/media/${mediaId}/search`, formData);
      setResult(res.data);
      if (res.data.found && videoRef.current) {
        videoRef.current.currentTime = res.data.timestamp;
        videoRef.current.play();
      }
    } catch (err) {
      console.error("Search failed", err);
      setResult({ found: false, reason: "Search failed. Check if a face is visible in the image." });
    } finally {
      setSearching(false);
    }
  };

  const videoUrl = `${API_URL}/uploads/${mediaId}.mp4`;

  return (
    <div className="min-h-screen px-6 py-8 md:px-12 lg:px-24">
      {/* Top Nav */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="mb-8"
      >
        <button 
          onClick={() => router.push("/")}
          className="flex items-center gap-2 text-white/50 hover:text-white transition-colors group"
        >
          <ChevronLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span className="font-medium">Back to gallery</span>
        </button>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Main Video Area */}
        <div className="lg:col-span-2">
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="video-glow aspect-video glass rounded-3xl border border-white/5 overflow-hidden relative group"
          >
            <video 
              ref={videoRef}
              src={mediaInfo ? `${API_URL}${mediaInfo.url}` : ""}
              controls
              className="w-full h-full object-contain"
            />

          </motion.div>
          
          <div className="mt-8 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold tracking-tight mb-2">Analysis Result</h2>
              <p className="text-white/40 font-mono text-sm">{mediaId}</p>
            </div>
          </div>
        </div>

        {/* Sidebar / Search Panel */}
        <div className="flex flex-col gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass rounded-3xl p-8 border border-white/10"
          >
            <div className="flex items-center gap-3 mb-6 font-bold text-lg">
              <Search className="w-5 h-5 text-accent" />
              <h3>Face Search</h3>
            </div>

            <p className="text-sm text-white/50 mb-8 leading-relaxed">
              Upload a JPG of the face you want to find within this video.
            </p>

            <form onSubmit={handleSearch} className="flex flex-col gap-4">
              <label className="group relative cursor-pointer block">
                <input 
                  type="file" 
                  accept="image/jpeg,image/png" 
                  className="hidden" 
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
                <div className="h-40 glass group-hover:bg-white/5 transition-colors rounded-2xl flex flex-col items-center justify-center gap-3 border border-dashed border-white/20">
                  {file ? (
                    <img 
                      src={URL.createObjectURL(file)} 
                      className="w-full h-full object-cover rounded-2xl p-1" 
                    />
                  ) : (
                    <>
                      <Upload className="w-8 h-8 text-white/20" />
                      <span className="text-sm font-medium text-white/40">Drop JPG here</span>
                    </>
                  )}
                </div>
              </label>

              <button
                disabled={searching || !file}
                type="submit"
                className="bg-accent hover:bg-accent/90 disabled:opacity-50 text-white font-bold h-14 rounded-2xl transition-all flex items-center justify-center gap-3"
              >
                {searching ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    Find in Video
                  </>
                )}
              </button>
            </form>

            <AnimatePresence>
              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className={`mt-8 p-4 rounded-2xl border ${
                    result.found ? "bg-green-500/10 border-green-500/20" : "bg-red-500/10 border-red-500/20"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {result.found ? (
                      <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                    )}
                    <div>
                      <h4 className="font-bold text-sm">
                        {result.found ? "Face found!" : "No match found"}
                      </h4>
                      {result.found && (
                        <div className="mt-2 flex flex-col gap-1">
                          <p className="text-xs text-white/60">
                            Confidence: {((1 - (result.distance || 0)) * 100).toFixed(1)}%
                          </p>
                          <button 
                            onClick={() => {
                              if (videoRef.current) videoRef.current.currentTime = result.timestamp || 0;
                            }}
                            className="mt-2 flex items-center gap-2 text-xs font-bold text-accent hover:underline"
                          >
                            <Play className="w-3 h-3 fill-accent" />
                            Jump to {result.timestamp?.toFixed(2)}s
                          </button>
                        </div>
                      )}
                      {!result.found && (
                        <p className="text-xs text-white/60 mt-1 leading-relaxed">
                          {result.reason || "We couldn't find a confident match for this person in the video data."}
                        </p>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
