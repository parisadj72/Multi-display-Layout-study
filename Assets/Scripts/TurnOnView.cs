using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class TurnOnView : MonoBehaviour
{
    public GameObject viewLayout;
    private List<Transform> views = new List<Transform>();
    private int numberOfWindows;
    private Boolean isOn = false;

    public int trials = 5;

    private void Start()
    {
        InitializeLayout();
        RandomWindowOn();
    }

    private void RandomWindowOn()
    {
        int turnedOnWindow = UnityEngine.Random.Range(0, numberOfWindows);

        views[turnedOnWindow].GetComponent<Toggle>().isOn = true;
    }

    private void InitializeLayout()
    {
        foreach (Transform t in transform)
        {
            print(t.name);
            views.Add(t);
            numberOfWindows = views.Count;

        }
        print(numberOfWindows);
    }

    public void decreaseTrials()
    {
        if (isOn)
        {
        trials--;
        }
        print("Trials left: " +  trials);
    }
}
//t.GetComponent<Toggle>().isOn = true