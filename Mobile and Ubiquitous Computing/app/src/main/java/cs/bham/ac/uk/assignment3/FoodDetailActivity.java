package cs.bham.ac.uk.assignment3;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.google.android.material.bottomnavigation.BottomNavigationView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentTransaction;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageButton;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class FoodDetailActivity extends AppCompatActivity implements BottomNavigationView.OnNavigationItemSelectedListener  {
    private DetailAdapter ingr_detailsAdpt; //The Adapter for Ingredients on the Detail Activity
    private DetailAdapter step_detailsAdpt; //The Adapter for Steps on the Detail Activity
    private RecyclerView.LayoutManager ing_layoutManager;
    private RecyclerView.LayoutManager ste_layoutManager;
    public SharedPreferences Favourites; //How to store Favourited items

    PreferFragment pF = new PreferFragment();
    FavourFragment fF = new FavourFragment();
    AboutFragment aF = new AboutFragment();
    FragmentManager fm = getSupportFragmentManager();

    private int recID;
    private String mainName;
    public String Favourite = "Empty";

    private List<String> FavList = new ArrayList<String>();
    //public boolean isLongClick

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_food_detail);

        ingr_detailsAdpt = new DetailAdapter(Ingred);
        step_detailsAdpt = new DetailAdapter(Steps);
        RecyclerView ing_listView = (RecyclerView) findViewById(R.id.Det_Ingr);
        RecyclerView ste_listView = (RecyclerView) findViewById(R.id.Det_Step);

        ing_layoutManager = new LinearLayoutManager(this);
        ing_listView.setLayoutManager(ing_layoutManager);
        ing_listView.setAdapter(ingr_detailsAdpt);

        ste_layoutManager = new LinearLayoutManager(this);
        ste_listView.setLayoutManager(ste_layoutManager);
        ste_listView.setAdapter(step_detailsAdpt);


        recID = getIntent().getIntExtra("RecID",0);
        //Log.i("Id", String.valueOf(recID));
        mainName = getIntent().getStringExtra("name");
        //Log.i("name", String.valueOf(mainName));
        RequestQueue requestQueue = Volley.newRequestQueue(getApplicationContext());
        JsonObjectRequest getRequest = new JsonObjectRequest(Request.Method.GET, " https://www.sjjg.uk/eat/recipe-details/" + recID, null, new Response.Listener<JSONObject>() {
            @Override
            public void onResponse(JSONObject response) {
                TextView name = findViewById(R.id.Det_Name);
                TextView desc = findViewById(R.id.Det_Desc);
                //RecyclerView ingr = findViewById(R.id.Det_Ingr);
                //RecyclerView step = findViewById(R.id.Det_Step);
                try {
                    name.setText(mainName);
                    desc.setText(response.getString("description"));
                    JSONArray Ingredients = response.getJSONArray("ingredients");
                    JSONArray Steps = response.getJSONArray("steps");
                    //Log.i("ingredients", Ingredients.toString());
                    //Log.i("steps", Steps.toString());
                    populateLists(Ingredients,Steps);
                    //ingr.setText(response.getString("description")); Need to work out how to put json arry into recycler
                    //ingr.setText(response.getString("description"));
                } catch (JSONException err) {
                }
            }
        },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {}
                }
        );
        requestQueue.add(getRequest);
        ((BottomNavigationView)findViewById(R.id.bottom_navi)).setOnNavigationItemSelectedListener(this);

        //Favourite = (String) getIntent().getStringExtra("Favourites");
        ImageButton favbut = (ImageButton) findViewById(R.id.Det_Fave_Butt);
        favbut.setOnClickListener((new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        AddtoFavourite(v);
                    }
                })

        );
        favbut.setOnLongClickListener(new View.OnLongClickListener() {
            @Override
            public boolean onLongClick(View v) {
                RemoveFromFavourite(v);
                return true;
            }
        });
        Favourites = this.getSharedPreferences("fvs",Context.MODE_PRIVATE);
    }
    private ArrayList<String> Ingred = new ArrayList<String>();
    private ArrayList<String> Steps = new ArrayList<String>();
    private void populateLists(JSONArray Ing, JSONArray Ste) {
        Ingred.clear();
        Steps.clear();
        try {
            for (int i = 0; i < Ing.length(); i++) {
                //JSONObject jo = Ing.getJSONObject(i);
                Ingred.add(Ing.getString(i));

            }
            //int ingsize = Ingred.size();
            //Log.i("insize", String.valueOf(ingsize));
            //for(int k = 0; k < ingsize; k++){ Log.i("Ingr",Ingred.get(k));}
            for (int j = 0; j < Ste.length(); j++) {
                //JSONObject jo = Ste.getJSONObject(j);
                Steps.add(Ste.getString(j));
            }
           // int stepsize = Steps.size();
            //Log.i("stepsize", String.valueOf(stepsize));
            //for(int l = 0; l < ingsize; l++){ Log.i("Step",Steps.get(l));}
        } catch (JSONException err) {
            Log.i("Input Error", err.toString());
        }
        ingr_detailsAdpt.notifyDataSetChanged();
        step_detailsAdpt.notifyDataSetChanged();
    }

    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        FragmentTransaction fT = fm.beginTransaction();
        switch (item.getItemId())
        {
            case R.id.home:
                Intent intent = new Intent(this, MainActivity.class);
                //intent.putExtra("Favourites", Favourite);
                startActivity(intent);
                break;
            case R.id.preferences:
                fT.replace(R.id.frag_frame_det, pF);
                fT.addToBackStack(null);
                Log.i("Preferences Called","Preference fragment has been pressed");
                break;
            case R.id.favourites:
                fT.replace(R.id.frag_frame_det, fF);
                fT.addToBackStack(null);
                break;
            case R.id.about:
                fT.replace(R.id.frag_frame_det, aF);
                fT.addToBackStack(null);
                break;
        }
        fT.commit();
        return true;
    }
    public void PrefButtPress(View view) {
        //Log.i("Button", "Button Pressed");
        switch(view.getId()){
            case R.id.Pref_non:
                Log.i("None Radio","Radio Pressed");
                break;
            case R.id.Pref_bre:
                Log.i("Breakfast Radio","Radio Pressed");
                break;
            case R.id.Pref_lun:
                Log.i("Lunch Radio","Radio Pressed");
                break;
            case R.id.Pref_din:
                Log.i("Dinner Radio","Radio Pressed");
                break;
            case R.id.Pref_non2:
                Log.i("None2 Radio","Radio Pressed");
                break;
            case R.id.Pref_asc:
                Log.i("asc Radio","Radio Pressed");
                break;
            case R.id.Pref_des:
                Log.i("desc Radio","Radio Pressed");
                break;
            default:
                Log.i("Other","Other Button Pressed");
                break;
        }
    }
    public void AddtoFavourite(View view){
        //Log.i("PassedName",mainName);
        //Log.i("PassedName",Favourite);
        Favourites = this.getSharedPreferences("fvs",Context.MODE_PRIVATE);
        Favourite = Favourites.getString("Fave", "Empty");
        Log.i("PassedName",Favourite);
        SharedPreferences.Editor FavEdit = Favourites.edit();
        if (Favourite.contains(mainName)){} //Already Favourited
        else{
            if (Favourite.contains("Empty")){
                Favourite = Favourite.replaceAll("Empty,", "");
                Favourite = Favourite.replaceAll("Empty", "");
            } //If adding first favourite to empty list, remove the empty part
            String Temp = mainName + "," + Favourite;
            FavEdit.putString("Fave", Temp);
        }
        FavEdit.commit();
        Log.i("Favourite Added",Favourite);
        //String Temp[] = Favourite.split("|");
        //FavList = Arrays.asList(Temp);
        //System.out.println(Temp);


    }//RemoveFromFavourite
    public void RemoveFromFavourite(View view){
        //Log.i("PassedName",mainName);
        //Log.i("PassedName",Favourite);
        Favourite = Favourites.getString("Fave", "Empty");
        Log.i("PassedName",mainName);
        SharedPreferences.Editor FavEditLong = Favourites.edit();
        if (Favourite.contains(mainName)){
            String Temp =  mainName + ",";
            Favourite = Favourite.replaceAll(Temp, "");
            Favourite = Favourite.replaceAll(mainName, "");
            FavEditLong.putString("Fave", Favourite);
        } //Already Favourited
        else{
        }
        if (Favourite == "" || Favourite == ","){Favourite = "Empty";}
        FavEditLong.commit();
        Log.i("Favourite Removed",Favourite);
        //String Temp[] = Favourite.split("|");
        //FavList = Arrays.asList(Temp);
        //System.out.println(Temp);


    }
    /*private ArrayList<RecipeViewer> Ingred = new ArrayList<RecipeViewer>();
    private ArrayList<RecipeViewer> Steps = new ArrayList<RecipeViewer>();
    private void populateLists(JSONArray Ing, JSONArray Ste){
        Ingred.clear();
        Steps.clear();
        try{
            for (int i =0; i<Ing.length();i++) {
                JSONObject jo = Ing.getJSONObject(i);
                Ingred.add(new RecipeViewer(jo.getString(String.valueOf(i)), 0));

            }
            //int ingsize = Ingred.size();
            //for(int k = 0; k < ingsize; k++){ Log.i("Ingr",Ingred.get(k));}
            for (int j =0; j<Ste.length();j++) {
                JSONObject jo = Ste.getJSONObject(j);
                Steps.add(new RecipeViewer(jo.getString(String.valueOf(j)), 1));
            }
        }
        catch(JSONException err){Log.i("Input Error", err.toString());}
        ingr_detailsAdpt.notifyDataSetChanged();
        step_detailsAdpt.notifyDataSetChanged();
    }*/
}
