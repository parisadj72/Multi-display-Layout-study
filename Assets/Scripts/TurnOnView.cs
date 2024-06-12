using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor.PackageManager.UI;
using UnityEngine;
using UnityEngine.UI;

public class TurnOnView : MonoBehaviour
{
    public GameObject viewLayout;
    private View view;
    private List<View> views = new List<View>();

    private int numberOfWindows;
    public static int trials = 5;

    private void Start()
    {
        InitializeLayout();
        RandomWindowOn();
        RandomWindowOn();
        RandomWindowOn();
    }
    private void InitializeLayout()
    {
        Transform[] childTransforms = GetComponentsInChildren<Transform>();

        foreach (Transform childTransform in childTransforms)
        {
            View view = childTransform.GetComponent<View>();

            if (view != null)
            {
                views.Add(view);
            }
        }
        numberOfWindows = views.Count;
        //print(numberOfWindows);
    }

    private void RandomWindowOn()
    {
        int turnedOnWindow = UnityEngine.Random.Range(0, numberOfWindows);
        views[turnedOnWindow].TurnOn(true);
    }

    private void TraverseList(List<Transform> list)
    {
        foreach (Transform t in list)
        {
            print(t.name);
        }
    }


    //public void decreaseTrials()
    //{
    //    if (view.IsOn)
    //    {
    //        trials--;
    //    }
    //    print("Trials left: " + trials);
    //}
}
//t.GetComponent<Toggle>().isOn = true