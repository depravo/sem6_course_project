package com.depravo.musicapp.ui

import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ProgressBar
import android.widget.Toast
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.depravo.musicapp.R
import com.depravo.musicapp.network.ApiManager
import com.depravo.musicapp.data.*

private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

/**
 * A simple [Fragment] subclass.
 * Use the [Page3.newInstance] factory method to
 * create an instance of this fragment.
 */
class Page3 : Fragment() {
    private var param1: String? = null
    private var param2: String? = null
    private var recs = ArrayList<Song>()
    private var recsList: RecyclerView? = null
    private var adapter: SongAdapter? = null
    private val apiService = ApiManager()
    private var user: Int? = null
    private var recommendBtn: Button? = null
    private var recsProgressBar: ProgressBar? = null


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
        var view: View = inflater.inflate(R.layout.fragment_page3, container, false)
        user = MainActivity.user
        recommendBtn = view.findViewById(R.id.recommend_button)
        recsList = view.findViewById(R.id.recs_list)
        recsList!!.layoutManager = LinearLayoutManager(view.context)
        adapter = SongAdapter(view.context, recs)
        recsList!!.adapter = adapter
        recsProgressBar = view.findViewById(R.id.recs_loading)
        recommendBtn!!.setOnClickListener {
            recsProgressBar!!.visibility = View.VISIBLE
            apiService.getRecommendations(user!!) {
                if (it != null) {
                    recsProgressBar!!.visibility = View.GONE
                    recs.addAll(it)
                    adapter?.notifyDataSetChanged()
                } else {
                    recsProgressBar!!.visibility = View.GONE
                    Toast.makeText(
                        this.context,
                        "Server down",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }
        return view
    }

    companion object {
        /**
         * Use this factory method to create a new instance of
         * this fragment using the provided parameters.
         *
         * @param param1 Parameter 1.
         * @param param2 Parameter 2.
         * @return A new instance of fragment Page3.
         */
        @JvmStatic
        fun newInstance(param1: String, param2: String) =
            Page3().apply {
                arguments = Bundle().apply {
                    putString(ARG_PARAM1, param1)
                    putString(ARG_PARAM2, param2)
                }
            }
    }
}