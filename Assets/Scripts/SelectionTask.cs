using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class SelectionTask : MonoBehaviour
{
    private List<View> views = new List<View>();

    private int numberOfWindows;
    private int turnedOnWindow;
    public int trials = 5;

    private Boolean taskDone = false;

    public Boolean TaskDone
    {
        get { return taskDone; }
        set { taskDone = value; }
    }

    private void Start()
    {
        InitializeLayout();
        StartCoroutine(RandomWindowOn());
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

    IEnumerator RandomWindowOn()
    {
        for (int i = trials; i > 0; i--)
        {
            turnedOnWindow = UnityEngine.Random.Range(0, numberOfWindows);
            //print("Number was: " + turnedOnWindow);

            views[turnedOnWindow].TurnOn(true);
            //print("Window on is: " + (turnedOnWindow + 1));

            yield return new WaitUntil(() => !views[turnedOnWindow].IsOn);
        }
        print("Selection task is done");
        TaskDone = true;
    }

    private void TraverseList(List<View> list)
    {
        foreach (View view in list)
        {
            print(view.name);
        }
    }
}
