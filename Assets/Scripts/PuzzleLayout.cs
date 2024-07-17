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

    List<Texture> texlistOns = new List<Texture>();

    public List<View> Views { get => views; set => views = value; }
    public List<int> ModelOrder { get => modelOrder; set => modelOrder = value; }
    public List<Texture> TexlistOns { get => texlistOns; set => texlistOns = value; }

    private void Awake()
    {
        InitializeLayout();
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
                //print("View added");
            }
        }
    }

    public void CopyFields(List<Texture2D> texList, List<int> icons, List<int> viewOrder)
    {
        for (int i = 0; i < views.Count; i++)
        {
            modelTextures.Add(texList[i]);
            modelIcons.Add(icons[i]);
            modelOrder.Add(viewOrder[i]);
            //print(modelTextures[i].name);
        }

        for (int i = 0; i < views.Count; i++)
        {
            views[i].RawIcon.texture = modelTextures[modelIcons[i]];
            //print("Icons index: " + modelIcons[i]);
        }

        int selections = (views.Count / 3) + 1;

        for (int i = 0; i < selections; i++)
        {
            views[modelOrder[i]].TurnOn(true, false);
        }

        for (int i = 0; i < selections; i++)
        {
            texlistOns.Add(views[modelOrder[i]].RawIcon.texture);
        }

        List<Texture> copy = new List<Texture>();

        for (int i = 0; i < texlistOns.Count; i++)
        {
            Texture tex = texlistOns[i];
            copy.Add(tex);
        }

        texlistOns = RandomGenerator.shuffleList(texlistOns);

        if (copy.Equals(texlistOns)) {
            print("Lists are equal. Shuffle again");
        }

        //bool flag = true;
        //while (flag)
        //{
        //    for (int i = 0; i < texlistOns.Count; i++)
        //    {
        //        while (copy[i] != texlistOns[i])
        //        {
        //            flag = false;
        //        }
        //    }
        //    if (flag)
        //    {
        //        texlistOns = RandomGenerator.shuffleList(texlistOns);
        //    }
        //}


        for (int i = 0; i < selections; i++)
        {
            views[modelOrder[i]].RawIcon.texture = texlistOns[i];
        }
    }
}
