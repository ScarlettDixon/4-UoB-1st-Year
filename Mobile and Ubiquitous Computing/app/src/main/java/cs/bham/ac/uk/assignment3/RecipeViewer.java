package cs.bham.ac.uk.assignment3;

import org.json.JSONArray;

public class RecipeViewer {
    RecipeViewer(Integer a, String b, String c, Integer d){
        this.rec_ID = a;
        this.name = b;
        this.meal = c;
        this.time = d;
    }
    RecipeViewer(JSONArray a, JSONArray b){
        this.ingredients = a;
        this.steps = b;
    }
    RecipeViewer(String a, int b){
        if (b == 0){this.ingr = a;}
        else{this.step = a;}
    }

    private Integer rec_ID;
    private String name;
    private String meal;
    private Integer time;

    public Integer getRec_ID(){ return rec_ID;}
    public void setRec_ID(Integer inp){ rec_ID = inp;}
    public String getName(){ return name;}
    public void setName(String inp){ name = inp;}
    public String getMeal(){ return meal;}
    public void setMeal(String inp){ meal = inp;}
    public Integer getTime(){ return time;}
    public void setTime(Integer inp){ time = inp;}

    public String toName(){return getName();}
    public String toMeal(){return getMeal();}
    public Integer toTime(){return getTime();}


    private JSONArray ingredients;
    private JSONArray steps;
    public JSONArray getIngredients(){ return ingredients;}
    public JSONArray getSteps(){ return steps;}
    public String ingr;
    public String step;

}


