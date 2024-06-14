using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class SelectionTask : MonoBehaviour
{
    private View view;
    private List<View> views = new List<View>();

    private ToggleGroup toggleGroup;
    private int numberOfWindows;
    private int turnedOnWindow;
    public int trials = 5;

    private void Start()
    {
        toggleGroup = GetComponent<ToggleGroup>();
        toggleGroup.SetAllTogglesOff();
        InitializeLayout();
        //StartCoroutine(RandomWindowOn());
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

            views[turnedOnWindow].TurnOn(true);
            print("Window on is: " + (turnedOnWindow + 1));

            yield return new WaitUntil(() => !views[turnedOnWindow].IsOn);
        }

    }

    public void OnWindowClicked()
    {
        print("OnWindowClicked() called...");
        views[turnedOnWindow].TurnOff();
    }
    private void TraverseList(List<Transform> list)
    {
        foreach (Transform t in list)
        {
            print(t.name);
        }
    }
}
