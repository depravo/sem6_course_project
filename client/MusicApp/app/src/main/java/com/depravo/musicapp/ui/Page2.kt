package com.depravo.musicapp.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import android.widget.SearchView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.depravo.musicapp.R
import com.depravo.musicapp.data.*
import com.depravo.musicapp.network.ApiManager

private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

/**
 * A simple [Fragment] subclass.
 * Use the [Page2.newInstance] factory method to
 * create an instance of this fragment.
 */
class Page2 : Fragment(), SongListClickListener {
    private var param1: String? = null
    private var param2: String? = null
    private var songs = ArrayList<Song>()
    private var songList: RecyclerView? = null
    private var adapter: SongAdapter? = null
    private val apiService = ApiManager()
    private var user: Int? = null
    private var songSearchView: SearchView? = null

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
        songs.clear()
        var view: View = inflater.inflate(R.layout.fragment_page2, container, false)
        user = MainActivity.user
        songSearchView = view.findViewById(R.id.song_search_view)
        songList = view.findViewById(R.id.song_by_name_list)
        songSearchView!!.isSubmitButtonEnabled = true
        songList!!.layoutManager = LinearLayoutManager(view.context)
        adapter = SongAdapter(view.context, songs)
        adapter!!.clickListener = this@Page2
        songList!!.adapter = adapter
        songSearchView!!.setOnQueryTextListener(object : SearchView.OnQueryTextListener {
            override fun onQueryTextSubmit(query: String): Boolean {
                songs.clear()
                apiService.getSongsByName(query!!) {
                    if (it != null) {
                        songs.addAll(it)
                        adapter?.notifyDataSetChanged()

                    }
                }
                return false
            }

            override fun onQueryTextChange(newText: String): Boolean {
                songs.clear()
                adapter?.notifyDataSetChanged()
                return false
            }
        })
        return view
    }

    companion object {
        /**
         * Use this factory method to create a new instance of
         * this fragment using the provided parameters.
         *
         * @param param1 Parameter 1.
         * @param param2 Parameter 2.
         * @return A new instance of fragment Page2.
         */
        @JvmStatic
        fun newInstance(param1: String, param2: String) =
            Page2().apply {
                arguments = Bundle().apply {
                    putString(ARG_PARAM1, param1)
                    putString(ARG_PARAM2, param2)
                }
            }
    }

    override fun onItemClicked(index: Int) {
        val cred = AddingSongCredentials(user!!, songs[index].name)
        apiService.addSongToPlaylist(cred) {
            if (it != null) {
                if(it.success == true) {
                    songs.removeAt(index)
                    songList!!.adapter?.notifyDataSetChanged()
                }
                Toast.makeText(
                    this.context,
                    it?.message,
                    Toast.LENGTH_SHORT
                ).show()
            }
        }

    }

}