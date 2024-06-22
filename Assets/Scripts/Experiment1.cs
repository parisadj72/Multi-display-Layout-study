using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Experiment1 : MonoBehaviour
{
    public List<GameObject> layouts = new List<GameObject>();
    private void Awake()
    {
        
    }

    private void InitializeExperiment()
    {

        for (int i = 9; i >= 0; i--)
        {
            print("Doing first task...");

        }
    }

    IEnumerator WaitForTask()
    {
        print("Task in progress");

        yield return new WaitUntil(() => layouts[0].)
    }
}
