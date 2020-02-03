package com.example.magicclock.ui.dashboard

import android.Manifest
import android.content.pm.PackageManager
import android.location.Location
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProviders
import com.example.magicclock.R
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import java.net.URL

class DashboardFragment : Fragment() {
    private lateinit var fusedLocationClient: FusedLocationProviderClient

    private lateinit var dashboardViewModel: DashboardViewModel

    private lateinit var locationText: TextView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        dashboardViewModel =
                ViewModelProviders.of(this).get(DashboardViewModel::class.java)
        val root = inflater.inflate(R.layout.fragment_dashboard, container, false)
        val textView: TextView = root.findViewById(R.id.text_dashboard)
        locationText = root.findViewById(R.id.location_text)
        dashboardViewModel.text.observe(this, Observer {
            textView.text = it
        })

        val leftButton = root.findViewById<Button>(R.id.left_button)
        val rightButton = root.findViewById<Button>(R.id.right_button)
        val locationButton = root.findViewById<Button>(R.id.location_button)

        leftButton.setOnClickListener {
            GlobalScope.launch {
                goLeft()
            }
        }

        rightButton.setOnClickListener {
            GlobalScope.launch {
                goRight()
            }
        }

        locationButton.setOnClickListener {
            getLocation()
        }

        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this.requireActivity())

        return root
    }

    fun getLocation() {
        fusedLocationClient.lastLocation.addOnSuccessListener { location : Location? ->
            println(location.toString())
            locationText.text = location.toString()
        }
    }

    suspend fun goLeft() {
        URL("http://192.168.1.12:5000/move_left/1").readText()
    }

    suspend fun goRight() {
        URL("http://192.168.1.12:5000/move_right/1").readText()
    }
}