using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SelectionTask : MonoBehaviour
{
    private List<View> views = new List<View>();

    private int numberOfWindows;
    private int turnedOnWindow;
    public int trials = 5;

    private Boolean taskDone;

    public Boolean TaskDone
    {
        get { return taskDone; }
        set { taskDone = value; }
    }

    private void Awake()
    {
        InitializeLayout();
    }

    private void Start()
    {
        StartCoroutine(Task1());
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
        TaskDone = false;
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
        TaskDone = true;
    }

    IEnumerator Task1()
    {
        StartCoroutine(RandomWindowOn());
        yield return new WaitUntil(() => TaskDone);
        print("Task is finished");
        Destroy(this.gameObject, 5);
    }

    private void TraverseList(List<View> list)
    {
        foreach (View view in list)
        {
            print(view.name);
        }
    }
}
