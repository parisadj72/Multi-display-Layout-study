using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Experiment1 : MonoBehaviour
{
    public List<SelectionTask> layouts = new List<SelectionTask>();
    private List<int> randomLayouts = new List<int>();
    private int instantiatedLayout;
    private SelectionTask currentLayout;

    public enum Experiment { Exp1, Exp2, Exp3 };
    public Experiment experiment;

    private void Awake()
    {
        randomLayouts = RandomGenerator.randomizeList(layouts.Count);
    }
    private void Start()
    {
        StartCoroutine(WaitForTask());
    }

    IEnumerator WaitForTask()
    {
        print("Task in progress");

        for (int i = 0; i < randomLayouts.Count; i++)
        {
            instantiatedLayout = randomLayouts[i];
            Instantiate(layouts[instantiatedLayout], transform);

            currentLayout = GetComponentInChildren<SelectionTask>();

            yield return new WaitUntil(() => currentLayout.TaskDone);
            print(currentLayout.name);
            Destroy(currentLayout.gameObject, 5);
            yield return new WaitForSeconds(5);
            //StartCoroutine(TakeBreak(5));
        }
    }

    IEnumerator TakeBreak(int time)
    {
        //Learned something new today: Calling a coroutine to stop the 
        // execution of another one does not work. 
        // What stops is the coroutine you call. Not the calling coroutine
        yield return new WaitForSeconds(time);
    }

    private void LayoutInfo()
    {
        print(instantiatedLayout);
        print(layouts[instantiatedLayout].isActiveAndEnabled);
    }

    private void Update()
    {
        if (Input.GetKey(KeyCode.I))
        {
            LayoutInfo();
        }
    }

    private void TraverseList(List<SelectionTask> list)
    {
        foreach (SelectionTask selT in list)
        {
            print(selT.name);
        }
    }

    private void TraverseList(List<int> list)
    {
        foreach (int selT in list)
        {
            print(selT);
        }
    }
}
