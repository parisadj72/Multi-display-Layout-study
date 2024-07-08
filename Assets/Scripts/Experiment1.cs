using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Experiment1 : MonoBehaviour
{
    public List<SelectionTask> layouts = new List<SelectionTask>();
    private List<int> randomLayouts = new List<int>();
    private int instantiatedLayout;

    private void Awake()
    {
        RandomizeLayouts();
    }
    private void Start()
    {
        StartCoroutine(WaitForTask());
    }

    private void RandomizeLayouts()
    {
        // The randomLayouts list must be initialized to contain a first random number (layout in editor)
        // Otherwise we get a null object exception
        randomLayouts.Add(UnityEngine.Random.Range(0, layouts.Count));

        while (randomLayouts.Count < layouts.Count)
        {
            int randomLayout = UnityEngine.Random.Range(0, layouts.Count);
            if (randomLayouts.Contains(randomLayout))
            {
                continue;
            }
            else randomLayouts.Add(randomLayout);
        }
    }

    IEnumerator WaitForTask()
    {
        print("Task in progress");

        for (int i = 0; i < randomLayouts.Count; i++)
        {
            instantiatedLayout = randomLayouts[i];
            Instantiate(layouts[instantiatedLayout], transform);

            yield return new WaitUntil(() => transform.childCount == 0);
            StartCoroutine(TakeBreak(5));
        }
    }

    IEnumerator TakeBreak(int time)
    {
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
