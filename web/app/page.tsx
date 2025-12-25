"use client";

import { useState, useEffect } from "react";
import { Upload, Play, Film, Search, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Media {
  id: string;
  url: string;
}

export default function LandingPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [mediaList, setMediaList] = useState<Media[]>([]);
  const [loadingMedia, setLoadingMedia] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchMedia();
  }, []);

  const fetchMedia = async () => {
    try {
      const res = await axios.get(`${API_URL}/media`);
      setMediaList(res.data);
    } catch (err) {
      console.error("Failed to fetch media", err);
    } finally {
      setLoadingMedia(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${API_URL}/media`, formData);
      router.push(`/${res.data.media_id}`);
    } catch (err) {
      console.error("Upload failed", err);
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen px-6 py-12 md:px-12 lg:px-24">
      {/* Header */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-16"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-accent rounded-xl flex items-center justify-center">
            <Search className="text-white w-5 h-5" />
          </div>
          <h1 className="text-2xl font-bold tracking-tighter">FACET</h1>
        </div>
      </motion.header>

      {/* Hero / Upload */}
      <section className="max-w-4xl mx-auto mb-24 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-3xl p-12 border border-white/5 relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-accent/5 pointer-events-none" />
          
          <Film className="w-16 h-16 text-accent mx-auto mb-6 opacity-50" />
          <h2 className="text-4xl font-extrabold mb-4 tracking-tight">Process your video</h2>
          <p className="text-foreground/60 mb-8 max-w-md mx-auto">
            Upload any video and my AI pipeline will detect, track, and extract the best faces for you to search.
          </p>

          <form onSubmit={handleUpload} className="flex flex-col items-center gap-4">
            <label className="group relative cursor-pointer w-full max-w-sm">
              <input 
                type="file" 
                accept="video/*" 
                className="hidden" 
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              <div className="h-16 bg-white/5 group-hover:bg-white/10 transition-colors rounded-2xl flex items-center justify-center gap-3 px-6 border border-white/10">
                <Upload className="w-5 h-5 text-accent" />
                <span className="font-medium truncate">
                  {file ? file.name : "Select video file"}
                </span>
              </div>
            </label>

            <AnimatePresence>
              {file && (
                <motion.button
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  disabled={uploading}
                  type="submit"
                  className="bg-accent hover:bg-accent/90 disabled:opacity-50 text-white font-bold h-16 px-12 rounded-2xl transition-all flex items-center gap-3 shadow-xl shadow-accent/20"
                >
                  {uploading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      Start Analysis
                    </>
                  )}
                </motion.button>
              )}
            </AnimatePresence>
          </form>
        </motion.div>
      </section>

      {/* Gallery */}
      <section>
        <div className="flex items-center gap-3 mb-8">
          <h3 className="text-xl font-bold">Previous Content</h3>
          <span className="bg-white/5 px-3 py-1 rounded-full text-xs font-medium text-white/50">
            {mediaList.length} total
          </span>
        </div>

        {loadingMedia ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-white/20" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mediaList.map((m, idx) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <Link href={`/${m.id}`}>
                  <div className="glass rounded-2xl border border-white/5 group overflow-hidden cursor-pointer hover:border-accent/30 transition-all">
                    <div className="aspect-video bg-black relative">
                      <video 
                        src={`${API_URL}${m.url}#t=1`} 
                        className="w-full h-full object-cover opacity-50 group-hover:scale-110 transition-transform duration-500"
                      />
                      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <Play className="w-12 h-12 text-white fill-white" />
                      </div>
                    </div>
                    <div className="p-4 flex items-center justify-between">
                      <span className="text-sm font-mono text-white/40 truncate max-w-[200px]">{m.id}</span>
                      <span className="text-xs text-accent font-bold uppercase tracking-wider">Open</span>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
            {mediaList.length === 0 && (
              <div className="col-span-full py-24 text-center glass rounded-2xl border-dashed border-2 border-white/5">
                <p className="text-white/20">No videos found. Upload your first one above!</p>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
