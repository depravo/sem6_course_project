package com.depravo.musicapp.ui

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.depravo.musicapp.R
import com.depravo.musicapp.data.*
import com.squareup.picasso.Picasso

class SongAdapter internal constructor(context: Context?, private var songs: List<Song>) :
    RecyclerView.Adapter<SongAdapter.ViewHolder>() {
    private val inflater: LayoutInflater
    var clickListener: SongListClickListener? = null

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view: View = inflater.inflate(R.layout.list_item, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val song = songs[position]
        holder.bind(song, position)

    }

    override fun getItemCount(): Int {
        return songs.size
    }

    inner class ViewHolder(val view: View) : RecyclerView.ViewHolder(view) {

        fun bind(song: Song, position: Int) {
            val logoView = view.findViewById<ImageView>(R.id.song_logo)
            val nameView = view.findViewById<TextView>(R.id.song_name)
            val artistsView = view.findViewById<TextView>(R.id.song_artist)
            Picasso.get().load(song.logoResource).into(logoView)
            nameView.text = song.name
            artistsView.text = song.artist
            view.setOnClickListener { clickListener!!.onItemClicked(position) }
        }
    }

    init {
        inflater = LayoutInflater.from(context)
    }
}