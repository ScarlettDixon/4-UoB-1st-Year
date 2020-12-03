package cs.bham.ac.uk.assignment3;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentTransaction;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.Volley;
import com.google.android.material.bottomnavigation.BottomNavigationView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Map;
import java.util.Set;

public class MainActivity extends AppCompatActivity implements BottomNavigationView.OnNavigationItemSelectedListener{
    //OnFragmentInteractionListener
    private RecipesAdapter recipesAdpt;
    private RecyclerView.LayoutManager layoutManager;
    private SharedPreferences Meals;
    private SharedPreferences Times;
    public String Favourite = "Empty";

    PreferFragment pF = new PreferFragment();
    FavourFragment fF = new FavourFragment();
    AboutFragment aF = new AboutFragment();
    FragmentManager fm = getSupportFragmentManager();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Meals = this.getPreferences(Context.MODE_PRIVATE);
        Times = this.getPreferences(Context.MODE_PRIVATE);

        recipesAdpt = new RecipesAdapter(recipes);
        RecyclerView listView = (RecyclerView) findViewById(R.id.Main_FoodItems);

        layoutManager = new LinearLayoutManager(this);
        listView.setLayoutManager(layoutManager);
        listView.setAdapter(recipesAdpt);

        String Web = "https://www.sjjg.uk./eat/food-items";
        String Question="";
        String Meal="";
        String And="";
        String Order="";
        String URL = Web+Question+Meal+And+Order;
        switch(Meals.getString("meal","Failed")){
            case "None": Question="";Meal = "";break;
            case "Breakfast": Question="?";Meal = "prefer=Breakfast";break;
            case "Lunch": Question="?";Meal = "prefer=Lunch";break;
            case "Dinner": Question="?";Meal = "prefer=Dinner";break;
            default: Meal = "";break;
        }
        switch(Times.getString("meal","Failed")){
            case "None": Order = "";break;
            case "Ascending": Question="?";Order = "ordering=asc";break;
            case "Descending": Question="?";Order = "ordering=desc";break;
            default: Order = "";break;
        }
        if (Meal != "" && Order !=""){And = "&";}
        URL = Web+Question+Meal+And+Order;
        Log.i("Url", URL);
        RequestQueue rQ = Volley.newRequestQueue(getApplicationContext());

        JsonArrayRequest getr = new JsonArrayRequest(Request.Method.GET, URL, null, new Response.Listener<JSONArray>() {
            @Override
            public void onResponse(JSONArray response) {
                //Log.i("Response", response.toString());
                populateList(response);
            }},
                new Response.ErrorListener()
                {
                    @Override
                    public void onErrorResponse(VolleyError error){}
                }
        );
        rQ.add(getr);



        ((BottomNavigationView)findViewById(R.id.bottom_navi)).setOnNavigationItemSelectedListener(this);
        //fm.beginTransaction().add(R.id.frag_frame,pF).commit();
        //Log.i("Meals", Meals.getString("meal","Failed"));
        //Log.i("Times", Meals.getString("time","Failed"));

        //Favourite = savedInstanceState.getString("Favourite");
        //Favourite = (String) getIntent().getStringExtra("Favourites");
        SharedPreferences Favourites = getSharedPreferences("fvs",Context.MODE_PRIVATE);
        Favourite = Favourites.getString("Fave", "" + "Empty");

    }

    /*public void onRecipeChoice(View view){


        RequestQueue rQ = Volley.newRequestQueue(getApplicationContext());
        JsonArrayRequest getr = new JsonArrayRequest(Request.Method.GET, "https://www.sjjg.uk./eat/food-items", null, new Response.Listener<JSONArray>() {
                    @Override
                    public void onResponse(JSONArray response) {
                        //Log.i("Response", response.toString());
                        populateList(response);
                    }},
                new Response.ErrorListener()
                {
                    @Override
                    public void onErrorResponse(VolleyError error){}
                }
                );
        rQ.add(getr);
    }*/
    private ArrayList<RecipeViewer> recipes = new ArrayList<RecipeViewer>(); //Creates empty arraylist
    private void populateList(JSONArray items){ //Takes in the JSON array, called when button pressed or on create
        recipes.clear(); //Clears the arraylist
        try{
            for (int i =0; i<items.length();i++) {
                JSONObject jo = items.getJSONObject(i); //Goes through evey item in the JSONARRAY
                recipes.add(new RecipeViewer(jo.getInt("id"),jo.getString("name"),jo.getString("meal"), jo.getInt("time"))); //Splits up data and sends it to RecipeViewer
            }
        }
        catch(JSONException err){}
        recipesAdpt.notifyDataSetChanged();
    }

    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        FragmentTransaction fT = fm.beginTransaction();
        switch (item.getItemId())
        {
            case R.id.home:
                //fT.addToBackStack(null);
                //getSupportFragmentManager().popBackStack();
                //fT.remove(R.id.frag_frame);
                //Fragment frag = fm.findFragmentById(R.id.frag_frame);
                //fT.remove(frag);
                //if(fm.getBackStackEntryCount()>0) {
                //    for (int i = 0; i < fm.getBackStackEntryCount(); ++i) {
                //        fm.popBackStack();
                //    }
                //}
                Intent intent = new Intent(this, MainActivity.class);
                //intent.putExtra("Favourites", Favourite); //Send through favourites so it is updateable when returning to main
                startActivity(intent);
                //Log.i("Home Called","Home fragment has been pressed");
                break;
            case R.id.preferences:
                fT.replace(R.id.frag_frame, pF);
                fT.addToBackStack(null);
                break;
            case R.id.favourites:
                fT.replace(R.id.frag_frame, fF);
                fT.addToBackStack(null);
                break;
            case R.id.about:
                fT.replace(R.id.frag_frame, aF);
                fT.addToBackStack(null);
                //Log.i("About Called","About fragment has been pressed");
                break;
        }
        fT.commit();
        return true;
    }
    public void PrefButtPress(View view) {
        //Log.i("Button", "Button Pressed");
        SharedPreferences.Editor mealedit = Meals.edit();
        SharedPreferences.Editor timeedit = Times.edit();
        switch(view.getId()){
            case R.id.Pref_non:
                Log.i("None Radio","Radio Pressed");
                mealedit.putString("meal", "None");
                break;
            case R.id.Pref_bre:
                Log.i("Breakfast Radio","Radio Pressed");
                mealedit.putString("meal", "Breakfast");
                break;
            case R.id.Pref_lun:
                Log.i("Lunch Radio","Radio Pressed");
                mealedit.putString("meal", "Lunch");
                break;
            case R.id.Pref_din:
                Log.i("Dinner Radio","Radio Pressed");
                mealedit.putString("meal", "Dinner");
                break;
            case R.id.Pref_non2:
                Log.i("None2 Radio","Radio Pressed");
                timeedit.putString("time", "None");
                break;
            case R.id.Pref_asc:
                Log.i("asc Radio","Radio Pressed");
                timeedit.putString("time", "Ascending");
                break;
            case R.id.Pref_des:
                Log.i("desc Radio","Radio Pressed");
                timeedit.putString("time", "Descending");
                break;
                default:
                    Log.i("Other","Other Button Pressed");
                    break;
        }
        mealedit.commit();
        timeedit.commit();
    }
}
