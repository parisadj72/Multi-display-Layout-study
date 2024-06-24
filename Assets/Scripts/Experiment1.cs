using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Experiment1 : MonoBehaviour
{
    public List<SelectionTask> layouts = new List<SelectionTask>();
    private void Awake()
    {
        StartCoroutine(WaitForTask());
    }

    IEnumerator WaitForTask()
    {
        print("Task in progress");
        int randomLayout;

        for (int i = 0; i < layouts.Count; i++)
        {
            randomLayout = UnityEngine.Random.Range(0, layouts.Count);
            Instantiate(layouts[randomLayout], new Vector3(1.54799998f, 1.27499998f, 0.0930000022f), Quaternion.identity);
            yield return new WaitUntil(() => layouts[randomLayout].TaskDone);
            Destroy(layouts[randomLayout]);

        }
    }

    private void TraverseList(List<SelectionTask> list)
    {
        foreach (SelectionTask selT in list)
        {
            print(selT.name);
        }
    }
}
