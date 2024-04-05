package com.depravo.musicapp.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.depravo.musicapp.R
import com.depravo.musicapp.network.ApiManager
import com.depravo.musicapp.data.*

private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

/**
 * A simple [Fragment] subclass.
 * Use the [Page1.newInstance] factory method to
 * create an instance of this fragment.
 */
class Page1 : Fragment() {
    private var param1: String? = null
    private var param2: String? = null
    private var songs = ArrayList<Song>()
    private var songList: RecyclerView? = null
    private var adapter: SongAdapter? = null
    private val apiService = ApiManager()
    private var user: Int? = null
    private var refreshBtn: ImageButton? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            param1 = it.getString(ARG_PARAM1)
            param2 = it.getString(ARG_PARAM2)
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        var view: View = inflater.inflate(R.layout.fragment_page1, container, false)
        songList = view.findViewById(R.id.song_list)
        refreshBtn = view.findViewById(R.id.refresh_button)
        songList!!.layoutManager = LinearLayoutManager(view.context)
        adapter = SongAdapter(view.context, songs)
        songList!!.adapter = adapter
        refreshBtn!!.setOnClickListener{
            songs.clear()
            uploadPlaylist()
        }
        user = MainActivity.user
        uploadPlaylist()
        return view
    }

    fun uploadPlaylist() {
        apiService.getPlaylist(user!!) {
            if (it != null) {
                songs.addAll(it)
                songList!!.adapter?.notifyDataSetChanged()
            } else {
                Toast.makeText(
                    this.context,
                    "Server down",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }


    companion object {
        /**
         * Use this factory method to create a new instance of
         * this fragment using the provided parameters.
         *
         * @param param1 Parameter 1.
         * @param param2 Parameter 2.
         * @return A new instance of fragment Page1.
         */
        @JvmStatic
        fun newInstance(param1: String, param2: String) =
            Page1().apply {
                arguments = Bundle().apply {
                    putString(ARG_PARAM1, param1)
                    putString(ARG_PARAM2, param2)
                }
            }
    }
}