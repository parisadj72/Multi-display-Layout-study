using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using UnityEngine;

public class PuzzleLayout : MonoBehaviour
{
    private List<View> views = new List<View>();
    private List<Texture2D> modelTextures = new List<Texture2D>();
    private List<int> modelIcons = new List<int>();
    private List<int> modelOrder = new List<int>();

    private void Awake()
    {
        InitializeLayout();
    }
    void Start()
    {
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
                print("View added");
            }
        }
    }

    public void CopyFields(List<Texture2D> texList, List<int> icons, List<int> viewOrder)
    {
        for (int i = 0; i < views.Count; i++)
        {
            modelTextures.Add(texList[i]);
            print(modelTextures[i].name);
        }

        for (int i = 0; i < views.Count; i++)
        {
            modelIcons.Add(icons[i]);
            print("Icons index: " + modelIcons[i]);
        }

        for (int i = 0; i < views.Count; i++)
        {
            modelOrder.Add(viewOrder[i]);
            print("windows on: " + viewOrder[i]);
        }

        for (int i = 0; i < views.Count; i++)
        {
            views[modelOrder[i]].TurnOn(true, false);
        }
    }
}
